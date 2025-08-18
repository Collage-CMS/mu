#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier
# to produce XML strings.
#
#    mu.xml(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
from __future__ import annotations

import re
from typing import Callable
from typing import Union

from mu import util

ERR_NOT_ELEMENT_NODE = ValueError("Not an element node.")

ATOMIC_VALUE = {int, str, float, complex, bool, str}


class Node:
    """Base class for active markup nodes."""

    def __init__(self, name, *nodes, **attrs) -> None:
        self.set_name(name)
        self._attrs = {}
        if "cls" in attrs:
            attrs["class"] = attrs.pop("cls")
        self.set_attrs(attrs)
        self.replace(list(nodes))

    @property
    def tag(self) -> Union[str, Callable]:
        return self._name

    @property
    def attrs(self) -> dict:
        return self._attrs

    @property
    def content(self) -> list:
        return self._content

    def set_name(self, name: str) -> None:
        self._name = name

    def set_attr(self, name, value=None) -> None:
        self._attrs[name] = value

    def set_attrs(self, attrs: dict) -> None:
        self._attrs |= attrs

    def replace(self, nodes: list) -> None:
        self._content = nodes

    def append(self, *nodes: list) -> None:
        self._content.extend(nodes)

    def __repr__(self):
        return f"<{self.tag}...>"

    def __call__(self, *nodes, **attrs) -> list:
        mu = []
        mu.append(self.tag)
        if "cls" in attrs:
            attrs["class"] = attrs.pop("cls")
        attrs = self.attrs | attrs
        if len(attrs) > 0:
            mu.append(attrs)
        if len(self.content) > 0:
            mu.extend(self.content)
        if len(nodes) > 0:
            mu.extend(nodes)
        return mu


class Element(Node):
    def __init__(self, name: str, *nodes, **attrs) -> None:
        super().__init__(name, *nodes, **attrs)


class Text(Node):
    def __init__(self, *nodes) -> None:
        super().__init__("$text", *nodes)


class PI(Node):
    def __init__(self, *nodes) -> None:
        super().__init__("$pi", *nodes)


class CData(Node):
    def __init__(self, *nodes) -> None:
        super().__init__("$cdata", *nodes)


class Raw(Node):
    def __init__(self, *nodes) -> None:
        super().__init__("$raw", *nodes)


class Comment(Node):
    def __init__(self, *nodes) -> None:
        super().__init__("$comment", *nodes)


class SugarNames:
    def transform(self, node: list) -> list:
        if _is_element(node):
            if self._is_sugared_name(node[0]):
                tag = self._sugar_name(node[0])
                attributes = self._sugar_attrs(node[0])
                for name, value in attrs(node).items():
                    if "id" in attributes and name == "id":
                        pass
                    elif "class" in attributes and name == "class":
                        if isinstance(value, list):
                            attributes["class"].extend(value)
                        else:
                            attributes["class"].append(value)
                    else:
                        attributes[name] = value
                child_nodes = content(node)
                unsugared_node = []
                unsugared_node.append(tag)
                if len(attributes) > 0:
                    unsugared_node.append(attributes)
                if len(child_nodes) > 0:
                    unsugared_node.extend(child_nodes)
                return unsugared_node
            else:
                return node
        else:
            return node

    def _is_sugared_name(self, tag: str) -> bool:
        return "#" in tag or "." in tag

    def _sugar_name(self, tag: str) -> str:
        return re.split(r"[#.]", tag)[0]

    def _sugar_attrs(self, tag: str) -> dict:
        id = []
        cls = []
        for part in re.findall("[#.][^#.]+", tag):
            if part.startswith("#"):
                id.append(part[1:])
            elif part.startswith("."):
                cls.append(part[1:])
        attrs = {}
        if id:
            attrs["id"] = id[0]
        if cls:
            attrs["class"] = cls
        return attrs


class XmlSerializer:
    def __init__(self):
        self._names = SugarNames()

    def write(self, *nodes):
        return "".join(self._ser_sequence(list(nodes)))

    def _ser_node(self, node):
        if _is_element(node):
            yield from self._ser_element(node)
        elif _is_sequence(node):
            yield from self._ser_sequence(node)
        elif _is_active_node(node):
            yield from self._ser_node(node(*node.content, **node.attrs))
        else:
            yield from self._ser_atomic(node)

    def _ser_element(self, node):
        if _is_active_element(node):
            yield from self._ser_active_element(node)
        elif _is_special_node(node):
            yield from self._ser_special_node(node)
        else:
            node = self._names.transform(node)
            if _is_empty_node(node):
                yield from self._ser_empty_node(node)
            else:  # content to process
                yield from self._ser_content_node(node)

    def _start_tag(self, node, close: bool = False):
        node_tag = tag(node)
        if close is True:
            return f"<{node_tag}{self._ser_attrs(node)}/>"
        return f"<{node_tag}{self._ser_attrs(node)}>"

    def _ser_content_node(self, node):
        yield self._start_tag(node, close=False)
        for child in content(node):
            if isinstance(child, tuple):
                for x in child:
                    yield from self._ser_node(x)
            else:
                for x in self._ser_node(child):
                    yield x
        yield f"</{tag(node)}>"

    def _ser_empty_node(self, node):
        yield self._start_tag(node, close=True)

    def _ser_active_element(self, node: Node):
        # active element, receives attributes and content
        # and then generates xml
        node_obj = tag_obj(node)
        node_obj.set_attrs(attrs(node))
        node_obj.append(content(node))
        yield self._ser_node(node_obj())

    def _ser_sequence(self, node):
        # a sequence, list would imply a malformed element
        for x in node:
            for y in self._ser_node(x):
                yield y

    def _ser_atomic(self, node):
        if node:
            if _is_active_element(node):
                yield self._ser_node(tag(node)())  # type: ignore
            else:
                yield str(node)
        else:
            pass

    def _ser_attrs(self, node) -> str:
        node_attrs = attrs(node)
        output = []
        for name, value in sorted(node_attrs.items()):
            if value is None:
                pass
            elif isinstance(value, bool):
                if value:
                    output.append(f' {name}="{name}"')
            elif isinstance(value, list | tuple):
                output.append(
                    f' {name}="{util.escape_html(" ".join([str(item) for item in value]))}"',  # noqa
                )
            else:
                output.append(f' {name}="{util.escape_html(value)}"')
        return "".join(output)

    def _ser_special_node(self, node: list) -> str:
        if tag(node) == "$comment":
            return f"<!-- {''.join(node[1:])} -->"
        elif tag(node) == "$cdata":
            return f"<![CDATA[{''.join(node[1:])}]]>"
        elif tag(node) == "$raw":
            return "".join(node[1:])
        elif tag(node) == "$pi":
            return f"<?{''.join(node[1:])}?>"
        else:
            return ""


class HtmlSerializer(XmlSerializer):
    pass


class XhtmlSerializer(XmlSerializer):
    pass


class SgmlSerializer(XmlSerializer):
    pass


def _is_element(value) -> bool:
    return (
        isinstance(value, list) and len(value) > 0 and isinstance(value[0], str | Node)
    )


def _is_special_node(value) -> bool:
    return _is_element(value) and isinstance(value[0], str) and value[0][0] == "$"


def is_empty(node) -> bool:
    return bool(len(node) == 1 or (len(node) == 2 and isinstance(node[1], dict)))


def has_attrs(value):
    return (
        _is_element(value)
        and len(value) > 1
        and isinstance(value[1], dict)
        and len(value[1]) > 0
    )


def get_attr(name, node, default=None):
    if _is_element(node):
        atts = attrs(node)
        if name in atts:
            return atts[name]
        return default
    raise ValueError(node)


# Accessor functions


def tag(node) -> str:
    """The tag string of the element."""
    if _is_element(node):
        return node[0]
    raise ERR_NOT_ELEMENT_NODE


def tag_obj(node) -> Node:
    """The tag object of the element."""
    if _is_element(node):
        return node[0]
    raise ERR_NOT_ELEMENT_NODE


def attrs(node) -> dict:
    """Dict with all attributes of the element.
    None if the node is not an element.
    """
    if _is_element(node):
        if has_attrs(node):
            return node[1]
        return {}
    raise ERR_NOT_ELEMENT_NODE


def content(node) -> list:
    if _is_element(node) and len(node) > 1:
        children = node[2:] if isinstance(node[1], dict) else node[1:]
        return [x for x in children if x is not None]
    return []


def _is_active_node(node) -> bool:
    return callable(node)


def _is_active_element(node) -> bool:
    if _is_element(node):
        return _is_active_node(tag(node))
    return _is_active_node(node)


def _is_sequence(node) -> bool:
    return isinstance(node, list | tuple)


def _is_empty_node(node) -> bool:
    return len(content(node)) == 0


def _expand_nodes(node):
    if _is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if _is_active_element(node):
            return node_tag(*node_content, **node_attrs)  # type: ignore
        mu = []
        mu.append(node_tag)
        if len(node_attrs) > 0:
            mu.append(node_attrs)
        mu.extend([_expand_nodes(child) for child in node_content])
        return mu
    if isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_expand_nodes(child))
        return mu
    if _is_active_node(node):
        return node()
    return node


def _apply_nodes(node, rules: dict):
    if _is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if node_tag in rules:
            if _is_active_element(rules[node_tag]):
                rule = rules[node_tag]
                return rule(*node_content, **node_attrs)
            return rules[node_tag]
        mu: list = [node_tag]
        if len(node_attrs) > 0:
            mu.append(node_attrs)
        mu.extend([_apply_nodes(child, rules) for child in node_content])
        return mu
    if isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_apply_nodes(child, rules))
        return mu
    return node


def expand(nodes):
    """Expand a Mu datastructure (invoking all Mu objects mu() method)."""
    return _expand_nodes(nodes)


def apply(nodes, rules: dict):
    """Expand a Mu datastructure replacing nodes that have a rule by invoking
    its value mu() method.
    """
    """Apply Mu transformation rules to one or more Mu datastructures.

    Args:
        *nodes: One or more Mu nodes to transform
        rules: Tag->transformation function

    Returns:
        Transformed Mu datastructure(s)

    Example:
        TODO
    """
    return _apply_nodes(nodes, rules)


def _markup(*nodes, serializer=XmlSerializer()):
    """Convert Mu datastructure(s) into a markup string.

    Args:
        *nodes: One or more Mu nodes to convert

    Returns:
        A string containing the markup representation

    Example:
        >>> markup(["div", {"class": "content"}, "Hello"])
        '<div class="content">Hello</div>'

    """
    return serializer.write(*nodes)


def xml(*nodes):
    """Render Mu as an XML formatted string."""
    return _markup(*nodes)


def html(*nodes):
    """Render Mu as an XML formatted string."""
    return _markup(*nodes, serializer=HtmlSerializer())


def xhtml(*nodes):
    """Render Mu as an XML formatted string."""
    return _markup(*nodes, serializer=XhtmlSerializer())


def sgml(*nodes):
    """Render Mu as an XML formatted string."""
    return _markup(*nodes, serializer=SgmlSerializer())


def _loads_content(nodes):
    if len(nodes) == 1:
        return loads(nodes[0])
    return [loads(node) for node in nodes]


def _loads_boolean(node):
    v = get_attr("value", node)
    if v == "true()":
        return True
    return False


def loads(node):
    """Create a Python value from a Mu value."""
    typ = type(node)
    if typ in ATOMIC_VALUE or node is None:
        return node
    elif typ is dict:
        # dicts in mu are attributes so only used for control
        pass
    elif typ is list:
        if _is_element(node):
            node_typ = get_attr("as", node, "string")
            if node_typ == "object":
                obj = {}
                i = 0
                for item in content(node):
                    i += 1
                    if _is_element(item):
                        item_key = get_attr("key", item, tag(item))
                        item_value = loads(item)
                    else:
                        item_key = i
                        item_value = loads(item)
                    obj[item_key] = item_value
                return obj
            if node_typ == "array":
                arr = []
                for item in content(node):
                    arr.append(loads(item))
                return arr
            if node_typ == "string":
                return _loads_content(content(node))
            if node_typ == "boolean":
                return _loads_boolean(node)
            if node_typ == "null":
                return None
            if node_typ == "number":
                return None
            return None

        li = []
        for i in node:
            li.append(loads(i))
        return li
    else:
        raise ValueError(f"Unknown node {node}")


def _dumps_none(key="_"):
    return [key, {"as": "null"}]


def _dumps_string(value, key="_"):
    return [key, value]


def _dumps_array(values, key="_"):
    arr = [key, {"as": "array"}]
    for value in values:
        arr.append(dumps(value, "_"))
    return arr


def _dumps_map(value, key="_"):
    obj = [key, {"as": "object"}]
    for key in value.keys():
        obj.append(dumps(value[key], key))
    return obj


def _dumps_integer(value, key="_"):
    return [key, {"as": "integer"}, value]


def _dumps_float(value, key="_"):
    return [key, {"as": "float"}, value]


def _dumps_complex(value, key="_"):
    return [key, {"as": "complex"}, value]


def _dumps_boolean(value, key="_"):
    return [key, {"as": "boolean", "value": "true()" if value is True else "false()"}]


def _dumps_object(value, key="_"):
    if hasattr(value, "mu") and callable(value.mu):
        return [key, {"as": "mu"}, value.mu()]
    return [key, {"as": "null"}]


def _dumps_fun(value, key="_"):
    v = value()
    if v is None:
        return [key, {"as": "null"}]
    return [key, {"as": "mu"}, v]


def dumps(value, key="_"):
    """Create a Mu value from a Python value."""
    typ = type(value)
    if value is None:
        return _dumps_none(key)
    if typ is int:
        return _dumps_integer(value, key)
    if typ is float:
        return _dumps_float(value, key)
    if typ is complex:
        return _dumps_complex(value, key)
    if typ is str:
        return _dumps_string(value, key)
    if typ is bool:
        return _dumps_boolean(value, key)
    if typ is list or typ is tuple:
        return _dumps_array(value, key)
    if typ is dict:
        return _dumps_map(value, key)
    if callable(value):
        return _dumps_fun(value, key)
    if isinstance(value, object):
        return _dumps_object(value, key)
    return value
