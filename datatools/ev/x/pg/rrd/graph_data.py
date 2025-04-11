from dataclasses import dataclass

from datatools.dbview.x.util.qualified_name import QualifiedName
from datatools.ev.x.pg.rrd.card_data import CardData
from datatools.ev.x.pg.rrd.graph_helper import transitive_reduction


@dataclass
class GraphData:
    nodes: dict[str, CardData]
    edges: list[tuple[QualifiedName, QualifiedName]]

    def with_reduced_edges(self):
        return GraphData(self.nodes, transitive_reduction(self.edges))