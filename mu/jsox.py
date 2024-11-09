from __future__ import annotations

from mu import _is_element
from mu import content
from mu import get_attr
from mu import tag


ATOMIC_VALUE = set([int, str, float, bool, str])


def _load_content(nodes):
    if len(nodes) == 0:
        return None
    elif len(nodes) == 1:
        return load(nodes[0])
    else:
        return [load(node) for node in nodes]


def _load_boolean(node):
    v = get_attr("value", node)
    if v == "true()":
        return True
    else:
        return False


def load(node):
    typ = type(node)
    if typ in ATOMIC_VALUE or node is None:
        return node
    elif typ == list:
        if _is_element(node):
            node_typ = get_attr("as", node, "string")
            if node_typ == "object":
                obj = {}
                i = 0
                for item in content(node):
                    i += 1
                    if _is_element(item):
                        item_key = get_attr("key", item, tag(item))
                        item_value = _load_content(content(item))
                    else:
                        item_key = i
                        item_value = load(item)
                    obj[item_key] = item_value
                return obj
            elif node_typ == "array":
                arr = []
                for item in content(node):
                    if _is_element(item):
                        item_value = _load_content(content(item))
                    else:
                        item_value = load(item)
                    arr.append(item_value)
                return arr
            # coming from XML nodes may be string but can be cast to specific type
            elif node_typ == "string":
                return _load_content(content(node))
            elif node_typ == "boolean":
                return _load_boolean(node)
            elif node_typ == "null":
                return None
            elif node_typ == "number":
                pass

        else:
            li = []
            for i in node:
                li.append(load(i))
            return li
    elif typ == dict:
        # dicts in mu are attributes so only used for control
        pass
    else:
        raise ValueError(f"Unknown node {node}")


def _dump_none(key="_"):
    return [key, {"as": "null"}]


def _dump_string(value, key="_"):
    return [key, value]


def _dump_array(values, key="_"):
    arr = [key, {"as": "array"}]
    for value in values:
        arr.append(dump(value, "_"))
    return arr


def _dump_map(value, key="_"):
    obj = [key, {"as": "object"}]
    for key in value.keys():
        obj.append(dump(value[key], key))
    return obj


def _dump_integer(value, key="_"):
    return [key, {"as": "integer"}, value]


def _dump_float(value, key="_"):
    return [key, {"as": "float"}, value]


def _dump_complex(value, key="_"):
    return [key, {"as": "complex"}, value]


def _dump_boolean(value, key="_"):
    return [key, {"as": "boolean", "value": "true()" if value is True else "false()"}]


def _dump_object(value, key="_"):
    if hasattr(value, "mu") and callable(getattr(value, "mu")):
        return [key, {"as": "mu"}, value.mu()]
    else:
        return [key, {"as": "null"}]


def _dump_fun(value, key="_"):
    v = value()
    if v is None:
        return [key, {"as": "null"}]
    else:
        return [key, {"as": "mu"}, v]


def dump(value, key="_"):
    """Create a Mu value from a Python value."""
    typ = type(value)
    if value is None:
        return _dump_none(key)
    elif typ == int:
        return _dump_integer(value, key)
    elif typ == float:
        return _dump_float(value, key)
    elif typ == complex:
        return _dump_complex(value, key)
    elif typ == str:
        return _dump_string(value, key)
    elif typ == bool:
        return _dump_boolean(value, key)
    elif typ == list or typ == tuple:
        return _dump_array(value, key)
    elif typ == dict:
        return _dump_map(value, key)
    elif callable(value):
        return _dump_fun(value, key)
    elif isinstance(value, object):
        return _dump_object(value, key)
    else:
        return value
