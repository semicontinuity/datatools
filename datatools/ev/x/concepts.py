from typing import Dict

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

        for concept, base_path in self.concepts.items():
            if prefix == base_path:
                return RestEntity(concept, entity_id)

    def fetch_json(self, entity: RestEntity):
        url = f'{self.protocol}://{self.host}/{self.concepts[entity.concept]}/{entity.entity_id}'
        response = requests.request('GET', url, headers=self.headers)
        if 200 <= response.status_code < 300:
            return response.json()
        else:
            raise Exception(f"Got status {response.status_code} for {url}")
