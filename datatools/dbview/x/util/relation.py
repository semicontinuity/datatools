from dataclasses import dataclass

from datatools.dbview.x.util.qualified_name import QualifiedName


@dataclass
class Relation:
    src: QualifiedName
    dst: QualifiedName
