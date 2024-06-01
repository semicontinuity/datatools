import json

from datatools.json2ansi_toolkit.ansi_toolkit import AnsiToolkit
from datatools.json.structure_discovery import Discovery
from datatools.json.util import to_jsonisable
from datatools.json2ansi_toolkit.default_style import default_style


def test__1():
    j = {
        "discrete_inputs": [
            {
                "address": 0,
                "contents": [
                    {
                        "alias": "WATER_LEAK_SENSOR__A",
                        "value": 1
                    },
                    {
                        "alias": "WATER_LEAK_SENSOR__B",
                        "value": 1
                    }
                ]
            }
        ],
        "coils": [
            {
                "address": 0,
                "contents": [
                    {
                        "alias": "COIL_0",
                        "value": 0
                    },
                    {
                        "alias": "COIL_1",
                        "value": 0
                    }
                ]
            }
        ]
    }

    toolkit = AnsiToolkit(Discovery(), default_style(), primitive_max_width=None)
    descriptor = toolkit.discovery.object_descriptor(j)
    print(json.dumps(to_jsonisable(descriptor), indent=4))

    uniform = descriptor.is_uniform()
    print(f"uniform={uniform}")

    item_is_uniform = descriptor.item_is_uniform()
    print(f"item_is_uniform={item_is_uniform}")

    item_is_dict = descriptor.item_is_dict()
    print(f"item_is_dict={item_is_dict}")

    inner_item = descriptor.inner_item()
    print(f"inner_item={inner_item}")

    toolkit.uniform_table_node2(j, descriptor)

    # node = toolkit.node(j, descriptor)
