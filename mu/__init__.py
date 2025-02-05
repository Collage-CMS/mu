#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier
# to produce XML strings.
#
#    mu.markup(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
from __future__ import annotations

import re
from typing import Dict
from typing import List

import mu.util as util


ERR_NOT_ELEMENT_NODE = ValueError("Not an element node.")

ATOMIC_VALUE = set([int, str, float, complex, bool, str])

SPECIAL_NODES: frozenset[str] = frozenset({"$raw", "$comment", "$cdata", "$pi"})


class Node:
    """Base class for active markup nodes."""

    def __init__(self, *nodes, **attrs) -> None:
        self._content: List = []
        self._attrs: Dict = {}
        self.replace(nodes)
        # Hack to get around using `class` as kw argument (use `cls` instead)
        if "cls" in attrs:
            attrs["class"] = attrs.pop("cls")
        self.set_attrs(attrs)

    def set_attr(self, name, value=None) -> None:
        self._attrs[name] = value

    def set_attrs(self, attrs={}) -> None:
        self._attrs |= attrs

    def replace(self, nodes=[]) -> None:
        self._content = []
        self._content.extend(nodes)

    def append(self, nodes=[]) -> None:
        self._content.extend(nodes)

    def mu(self):
        raise NotImplementedError


class XmlNames(object):

    def transform(self, node: list) -> list:
        return node


class HtmlNames(object):

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
                unsugared_node = [tag]
                if len(attributes) > 0:
                    unsugared_node.append(attributes)
                if len(child_nodes) > 0:
                    unsugared_node.extend(child_nodes)
                return unsugared_node
            else:
                return node
        else:
            return node

    def _is_sugared_name(self, tag: str):
        return "#" in tag or "." in tag

    def _sugar_name(self, tag: str):
        name = re.split(r"[#.]", tag)[0]
        return name

    def _sugar_attrs(self, tag: str):
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


class Serializer(object):

    def write(self, *nodes):
        return "".join(self._ser_sequence(nodes))


class XmlSerializer(Serializer):

    def __init__(self):
        self._names = XmlNames()

    def _ser_node(self, node):

        if _is_element(node):
            yield from self._ser_element(node)
        elif _is_sequence(node):
            yield from self._ser_sequence(node)
        elif _is_active_node(node):
            # drop content of this node to get handled by active node
            _attrs = attrs(node)
            _content = content(node)
            if _attrs is not None:
                node.set_attrs(_attrs)
            if _content is not None:
                # given content gets appended
                node.append(_content)
            yield self._ser_node(_expand_nodes(node.mu()))
        else:
            yield from self._ser_atomic(node)

    def _ser_element(self, node):
        if _is_active_element(node):
            yield from self._ser_active_element(node)
        elif _is_special_node(node):
            yield self._ser_special_node(node)
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
        else:
            return f"<{node_tag}{self._ser_attrs(node)}>"

    def _ser_content_node(self, node):
        yield self._start_tag(node, close=False)
        for child in content(node):
            if isinstance(child, tuple):
                for x in child:
                    for y in self._ser_node(x):
                        yield y
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
        yield self._ser_node(node_obj.mu())

    def _ser_sequence(self, node):
        # a sequence, list would imply a malformed element
        for x in node:
            for y in self._ser_node(x):
                yield y

    def _ser_atomic(self, node):
        if node:
            if _is_active_element(node):
                yield self._ser_node(tag(node).mu())
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
            elif isinstance(value, (list, tuple)):
                output.append(
                    f' {name}="{util.escape_html(" ".join([str(item) for item in value]))}"'  # noqa
                )
            else:
                output.append(f' {name}="{util.escape_html(value)}"')
        return "".join(output)

    def _ser_special_node(self, node: list) -> str:
        if tag(node) == "$raw":
            return "".join(node[1:])
        elif tag(node) == "$comment":
            return f'<!-- {"".join(node[1:])} -->'
        elif tag(node) == "$cdata":
            return f'<![CDATA[{"".join(node[1:])}]]>'
        elif tag(node) == "$pi":
            return f'<?{"".join(node[1:])}?>'
        else:
            return ""


class HtmlSerializer(XmlSerializer):

    def __init__(self):
        self._names = HtmlNames()


class XhtmlSerializer(XmlSerializer):
    pass


class SgmlSerializer(XmlSerializer):
    pass


def _is_element(value) -> bool:
    return (
        isinstance(value, list) and len(value) > 0 and isinstance(value[0], (str, Node))
    )


def _is_special_node(value) -> bool:
    return _is_element(value) and isinstance(value[0], str) and value[0][0] == "$"


def is_empty(node) -> bool:
    if len(node) == 1:
        return True
    elif len(node) == 2 and isinstance(node[1], dict):
        return True
    else:
        return False


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
        else:
            return default
    else:
        raise ValueError(node)


# Accessor functions


def tag(node) -> str:
    """The tag string of the element."""
    if _is_element(node):
        return node[0]
    else:
        raise ERR_NOT_ELEMENT_NODE


def tag_obj(node) -> Node:
    """The tag object of the element."""
    if _is_element(node):
        return node[0]
    else:
        raise ERR_NOT_ELEMENT_NODE


def attrs(node) -> dict:
    """Dict with all attributes of the element.
    None if the node is not an element."""
    if _is_element(node):
        if has_attrs(node):
            return node[1]
        else:
            return {}
    else:
        raise ERR_NOT_ELEMENT_NODE


def content(node) -> list:
    if _is_element(node) and len(node) > 1:
        children = node[2:] if isinstance(node[1], dict) else node[1:]
        return [x for x in children if x is not None]
    else:
        return []


def _is_active_node(node) -> bool:
    return hasattr(node, "xml") and callable(getattr(node, "xml"))


def _is_active_element(node) -> bool:
    if _is_element(node):
        return _is_active_node(tag(node))
    else:
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
            if len(node_attrs) > 0:
                node_tag.set_attrs(node_attrs)
            node_tag.append(node_content)
            return node_tag.mu()
        else:
            mu = [node_tag]
            if len(node_attrs) > 0:
                mu.append(node_attrs)
            mu.extend([_expand_nodes(child) for child in node_content])
            return mu
    elif isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_expand_nodes(child))
        return mu
    else:
        if _is_active_node(node):
            return node.mu()
        else:
            return node


def _apply_nodes(node, rules: dict):
    if _is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if node_tag in rules:
            if _is_active_element(rules[node_tag]):
                rule = rules[node_tag]
                if len(node_attrs) > 0:
                    rule.set_attrs(node_attrs)
                rule.append(node_content)
                return rule.mu()
            else:
                return rules[node_tag]
        else:
            mu = [node_tag]
            if len(node_attrs) > 0:
                mu.append(node_attrs)
            mu.extend([_apply_nodes(child, rules) for child in node_content])
            return mu
    elif isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_apply_nodes(child, rules))
        return mu
    else:
        return node


def expand(nodes):
    """Expand a Mu datastructure (invoking all Mu objects mu() method)."""
    return _expand_nodes(nodes)


def apply(nodes, rules: dict):
    """Expand a Mu datastructure replacing nodes that have a rule by invoking
    its value mu() method."""
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


def _markup(*nodes, serializer: Serializer):
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
    return _markup(*nodes, serializer=XmlSerializer())


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
    # if len(nodes) == 0:
    #    return None
    if len(nodes) == 1:
        return loads(nodes[0])
    else:
        return [loads(node) for node in nodes]


def _loads_boolean(node):
    v = get_attr("value", node)
    if v == "true()":
        return True
    else:
        return False


def loads(node):
    """Create a Python value from a Mu value."""
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
                        item_value = loads(item)
                    else:
                        item_key = i
                        item_value = loads(item)
                    obj[item_key] = item_value
                return obj
            elif node_typ == "array":
                arr = []
                for item in content(node):
                    arr.append(loads(item))
                return arr
            elif node_typ == "string":
                return _loads_content(content(node))
            elif node_typ == "boolean":
                return _loads_boolean(node)
            elif node_typ == "null":
                return None
            elif node_typ == "number":
                pass

        else:
            li = []
            for i in node:
                li.append(loads(i))
            return li
    elif typ == dict:
        # dicts in mu are attributes so only used for control
        pass
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
    if hasattr(value, "mu") and callable(getattr(value, "mu")):
        return [key, {"as": "mu"}, value.mu()]
    else:
        return [key, {"as": "null"}]


def _dumps_fun(value, key="_"):
    v = value()
    if v is None:
        return [key, {"as": "null"}]
    else:
        return [key, {"as": "mu"}, v]


def dumps(value, key="_"):
    """Create a Mu value from a Python value."""
    typ = type(value)
    if value is None:
        return _dumps_none(key)
    elif typ == int:
        return _dumps_integer(value, key)
    elif typ == float:
        return _dumps_float(value, key)
    elif typ == complex:
        return _dumps_complex(value, key)
    elif typ == str:
        return _dumps_string(value, key)
    elif typ == bool:
        return _dumps_boolean(value, key)
    elif typ == list or typ == tuple:
        return _dumps_array(value, key)
    elif typ == dict:
        return _dumps_map(value, key)
    elif callable(value):
        return _dumps_fun(value, key)
    elif isinstance(value, object):
        return _dumps_object(value, key)
    else:
        return value
