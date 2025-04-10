from dataclasses import dataclass

from datatools.dbview.x.util.qualified_name import QualifiedName
from datatools.ev.x.pg.rrd.card_data import CardData


@dataclass
class GraphData:
    nodes: dict[str, CardData]
    edges: list[tuple[QualifiedName, QualifiedName]]
