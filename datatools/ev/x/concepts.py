from typing import Dict, List, Hashable

import requests

from datatools.ev.x.types import RestEntity


class Concepts:
    concepts: Dict[str, str]
    protocol: str
    host: str

    def __init__(self, concepts: Dict, protocol: str, host: str, headers: Dict[str, str]) -> None:
        self.concepts = concepts
        self.protocol = protocol
        self.host = host
        self.headers = headers

    def parse_path(self, path: str):
        parts = path.split('/')
        if len(parts) < 2:
            raise ValueError(path)
        prefix = '/'.join(parts[:-1])
        entity_id = parts[-1]

        for concept_name, concept_def in self.concepts.items():
            if prefix == concept_def['path']:
                return RestEntity(concept_name, entity_id)

    def fetch_json(self, entity: RestEntity):
        concept_def = self.concepts[entity.concept]
        url = f'{self.protocol}://{self.host}/{concept_def["path"]}/{entity.entity_id}'
        response = requests.request('GET', url, headers=self.headers)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            raise Exception(f"Got status {response.status_code} for {url}")

    def find_link_concept(self, concept: str, path: List[Hashable]):
        concept_def = self.concepts[concept]
        for link in concept_def['links']:
            path_pattern = link['path_pattern']
            if self.path_matches(path, path_pattern):
                return link['concept']

    def path_matches(self, path: List[Hashable], pattern: List[Hashable]):
        if len(path) != len(pattern):
            return False
        for i in range(len(path)):
            p = pattern[i]
            e = path[i]
            if p is None:
                if type(e) is not int:
                    return False
            elif p != e:
                return False
        return True
