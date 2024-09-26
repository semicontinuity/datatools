from datatools.json.html.list_node import ListNode
from datatools.json.html.matrix_node import MatrixNode
from datatools.json.html.object_node import ObjectNode
from datatools.json.html.page_node import PageNode


class HtmlToolkit:

    def page_node(self, j, descriptor):
        return PageNode(self.node(j, descriptor), "", self)

    def node(self, j, descriptor):
        if descriptor.is_primitive():
            return self.primitive(j)
        elif descriptor.is_dict():
            return self.object_node(j, descriptor)
        elif descriptor.is_list():
            return self.list_of_multi_record(j, descriptor)
        elif descriptor.is_array() and descriptor.length == 1 and descriptor.item.is_dict():
            return self.list_of_single_record(j[0], descriptor.item)
        elif descriptor.is_array():
            if descriptor.item.is_array() and descriptor.length is not None and descriptor.item.length is not None:
                return self.matrix_node(j, descriptor)
            # elif descriptor.item.is_dict() and descriptor.length is not None:
            #     return self.uniform_table_node(j, descriptor.item)

    def primitive(self, j):
        return str(j)

    def list_of_single_record(self, element, element_descriptor):
        return ListNode([self.node(element, element_descriptor)], self)

    def list_of_multi_record(self, j, descriptor):
        return ListNode([self.node(j[index], descriptor.list[index]) for index in range(len(descriptor.list))], self)

    def object_node(self, j, descriptor):
        return ObjectNode(j, descriptor, True, self)

    def matrix_node(self, j, descriptor):
        return MatrixNode(j, descriptor.length, descriptor.item.length, self)

    # def uniform_table_node(self, j, item_descriptor):
    #     return UniformTableNode(j, item_descriptor, self)
