from dataclasses import dataclass


@dataclass(frozen=True)
class QualifiedName:
    qualifier: str
    name: str
