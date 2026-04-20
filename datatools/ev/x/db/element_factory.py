from datatools.ev.x.db.db_rich_node_factory import DbRichNodeFactory
from datatools.jv.model.JObject import JObject
from datatools.jv.model.j_element_factory import JElementFactory, set_last_in_parent, set_padding


class DbElementFactory(JElementFactory):

    def build_row_view(
            self,
            model: dict,
            references: dict[str, dict],
            table_pks: list[str],
            links: dict[str, dict],
            realm: 'RealmPg',
            rich_node_factory: DbRichNodeFactory,
    ) -> JObject:
        """
        references is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        links is dict: column_name -> { "concept":"...", "concept-pk":"..." }
        """
        e = JObject(model, None)
        e.options = self.options

        # NB can be both in links and PKs! Print PKs first.
        views = []
        rich_node_factory = DbRichNodeFactory(self.options, references, table_pks, links, realm)

        for k, v in model.items():
            node = rich_node_factory.make_rich_node(v, k)
            if node is not None:
                views.append(node)
            else:
                views.append(self.build_model(v, k))

        e.set_elements(set_last_in_parent(set_padding(views)))
        return e
