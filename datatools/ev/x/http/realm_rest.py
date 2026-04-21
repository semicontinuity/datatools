import urllib
from typing import Dict, Any
from urllib.parse import urlparse

import requests

from datatools.ev.app_types import Realm, EntityReference, View
from datatools.ev.x.http.types import RestEntity
from datatools.ev.x.http.view_rest_entity import ViewRestEntity
from datatools.ev.x.json_path_util import JsonPathUtil


class RealmRest(Realm):
    concepts: Dict[str, Any]
    protocol: str
    host: str

    def __init__(self, name: str, concepts: Dict[str, Any], protocol: str, host: str, headers: Dict[str, str]) -> None:
        super().__init__(name)
        self.concepts = concepts
        self.protocol = protocol
        self.host = host
        self.headers = headers

    def create_view(self, e_ref: EntityReference) -> View:
        if type(e_ref) is RestEntity:
            return ViewRestEntity(e_ref, self)

    def match_entity(self, path: str) -> RestEntity:
        for concept_name, concept_def in self.concepts.items():
            concept_path = concept_def['path']
            concept_path_parts = urlparse(concept_path)
            match = JsonPathUtil.path_match(path, concept_path_parts.path)
            if match is not None:
                return RestEntity(realm_name=None, concept=concept_name, variables=match)

    def fetch_json(self, entity: RestEntity):
        concept_def = self.concepts[entity.concept]
        concept_path = concept_def["path"]
        parsed_url = urlparse(concept_path)
        path = JsonPathUtil.replace_path_vars(parsed_url.path, entity.variables)
        query = '' if parsed_url.query == '' else '?' + parsed_url.query
        if query == '' and entity.query:
            query = '?' + urllib.parse.urlencode(entity.query)

        url = f'{self.protocol}://{self.host}/{path}{query}'
        response = requests.request('GET', url, headers=self.headers, verify=False)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            raise Exception(f"Got status {response.status_code} for {url}")

    def find_link_spec(self, concept: str, json_path: str):
        concept_def = self.concepts[concept]
        for link in concept_def['links']:
            match = JsonPathUtil.path_list_match(json_path.split('.'), link['json_path'].split('.'))
            if match is not None:
                return link['concept'], link['value'], link.get('values')

    def get_path_variables(self, concept: str):
        return JsonPathUtil.extract_path_variables(self.concepts[concept]['path'])
