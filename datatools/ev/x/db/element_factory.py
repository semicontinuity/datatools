from datatools.ev.x.db.db_rich_node_factory import DbRichNodeFactory
from datatools.jv.model.JObject import JObject
from datatools.jv.model.j_element_factory import JElementFactory


class DbElementFactory(JElementFactory):

    def build_row_view(
            self,
            model: dict,
            rich_node_factory: DbRichNodeFactory,
    ) -> JObject:
        return self.object(model, k=None, parent=None, parent_path=[], rich_node_factory=rich_node_factory.make_rich_node)
