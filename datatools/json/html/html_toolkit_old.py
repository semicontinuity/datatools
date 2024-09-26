from datatools.json.html.array_of_nestable_objects import ArrayOfNestableObjectsNode
from datatools.json.html.list_node import ListNode
from datatools.json.html.matrix_node import MatrixNode
from datatools.json.html.object_node_old import ObjectNode
from datatools.json.structure_analyzer import *


class OldToolkit:

    def __init__(self, tk) -> None:
        self.tk = tk

    def list_node(self, j, parent, in_array_of_nestable_obj: bool):
        result = ListNode(None, tk=self.tk)
        records = [self.node(subj, result, in_array_of_nestable_obj) for subj in j]
        result.records = records
        return result

    def node(self, j, parent, in_array_of_nestable_obj: bool):
        pruned = []
        # replace with path_in_array_of_nestable_obj: when exhausted, allow again
        if type(j) is dict:
            descriptor, path_of_leaf_to_count = obj_descriptor_and_path_counts(j)
            if descriptor is not None:
                if len(j) == 1:
                    descriptor = None
                else:
                    descriptor, pruned = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
            if descriptor is None or in_array_of_nestable_obj or len(j) <= 1:
                return ObjectNode(j, True, parent, in_array_of_nestable_obj, self, self.tk)
            else:
                # dict, where all entries have the same structure, i.e., array-like dict
                dict_node = ArrayOfNestableObjectsNode(parent, j.values(), descriptor, self.tk, self, pruned)
                dict_node.record_nodes = []
                for key, sub_j in j.items():
                    record_node = {name: self.node(value, dict_node, True) for name, value in sub_j.items()}
                    record_node['#'] = key
                    dict_node.record_nodes.append(record_node)
                return dict_node
        elif type(j) is list:
            descriptor, path_of_leaf_to_count = array_descriptor_and_path_counts(j)
            if descriptor is not None and not in_array_of_nestable_obj:
                descriptor, pruned = prune_sparse_leaves(descriptor, path_of_leaf_to_count, len(j))
            if descriptor is not None and not in_array_of_nestable_obj and len(j) > 1:
                array_node = ArrayOfNestableObjectsNode(parent, j, descriptor, self.tk, self, pruned)
                array_node.record_nodes = []
                for i, sub_j in enumerate(j):
                    record_node = {name: self.node(value, array_node, True) for name, value in sub_j.items()}
                    record_node['#'] = str(i)
                    array_node.record_nodes.append(record_node)
                return array_node
            else:
                width = array_is_matrix(j)
                return MatrixNode(j, parent, width) if width is not None else self.list_node(j, parent, in_array_of_nestable_obj)
        else:
            return j

