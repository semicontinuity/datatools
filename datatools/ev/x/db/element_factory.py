from datatools.ev.x.db.db_rich_node_factory import DbRichNodeFactory
from datatools.jv.model.JObject import JObject
from datatools.jv.model.j_element_factory import JElementFactory, set_last_in_parent, set_padding


class DbElementFactory(JElementFactory):

    def build_row_view(
            self,
            model: dict,
            rich_node_factory: DbRichNodeFactory,
    ) -> JObject:
        """
        references is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        links is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        """
        e = JObject(model, None)
        e.options = self.options

        views = []

        for k, v in model.items():
            node = rich_node_factory.make_rich_node(v, k)
            if node is not None:
                views.append(node)
            else:
                views.append(self.build_model(v, k, rich_node_factory=rich_node_factory.make_rich_node))

        e.set_elements(set_last_in_parent(set_padding(views)))
        return e
