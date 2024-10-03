from typing import Dict, List, Hashable, Any

import requests

from datatools.ev.x.http.types import RestEntity


class Concepts:
    concepts: Dict[str, Any]
    protocol: str
    host: str

    def __init__(self, concepts: Dict[str, Any], protocol: str, host: str, headers: Dict[str, str]) -> None:
        self.concepts = concepts
        self.protocol = protocol
        self.host = host
        self.headers = headers

    def match_entity(self, path: str) -> RestEntity:
        for concept_name, concept_def in self.concepts.items():
            match = self.path_match(path, concept_def['path'])
            if match is not None:
                return RestEntity(concept_name, match)

    def fetch_json(self, entity: RestEntity):
        concept_def = self.concepts[entity.concept]
        url = f'{self.protocol}://{self.host}/{self.replace_path_vars(concept_def["path"], entity.variables)}'
        response = requests.request('GET', url, headers=self.headers, verify=False)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            raise Exception(f"Got status {response.status_code} for {url}")

    def find_link_spec(self, concept: str, json_path: str):
        concept_def = self.concepts[concept]
        for link in concept_def['links']:
            match = Concepts.path_list_match(json_path.split('.'), link['json_path'].split('.'))
            if match is not None:
                return link['concept'], link['value']

    @staticmethod
    def path_match(path: str, pattern: str):
        return Concepts.path_list_match(path.split('/'), pattern.split('/'))

    @staticmethod
    def path_list_match(path_parts: List[str], pattern_parts: List[str]):
        if len(path_parts) != len(pattern_parts):
            return None
        path_vars = {}
        for i in range(len(path_parts)):
            p = pattern_parts[i]
            e = path_parts[i]
            if p == '*':
                continue
            elif p.startswith('{') and p.endswith('}'):
                path_vars[p.removeprefix('{').removesuffix('}')] = e
            elif p != e:
                return None
        return path_vars

    @staticmethod
    def replace_path_vars(pattern: str, path_vars: Dict[str, str]):
        parts = pattern.split('/')
        for i in range(len(parts)):
            p = parts[i]
            if p.startswith('{') and p.endswith('}'):
                parts[i] = path_vars[p.removeprefix('{').removesuffix('}')]
        return '/'.join(parts)

    def get_path_variables(self, concept: str):
        return self._extract_path_variables(self.concepts[concept]['path'])

    @staticmethod
    def _extract_path_variables(pattern: str):
        parts = pattern.split('/')
        path_vars = set()
        for i in range(len(parts)):
            p = parts[i]
            if p.startswith('{') and p.endswith('}'):
                path_vars.add(p.removeprefix('{').removesuffix('}'))
        return path_vars
