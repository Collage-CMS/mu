#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier
# to produce XML strings.
#
#    mu.markup(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
from __future__ import annotations

from enum import auto
from enum import Enum

import mu.util as util


class Mode(Enum):
    XML = auto()
    XHTML = auto()
    HTML = auto()
    SGML = auto()


VOID_TAGS: frozenset[str] = frozenset(
    {
        "area",
        "base",
        "br",
        "col",
        "command",
        "embed",
        "hr",
        "img",
        "input",
        "keygen",
        "link",
        "meta",
        "param",
        "source",
        "track",
        "wbr",
    }
)

SPECIAL_NODES: frozenset[str] = frozenset({"$raw", "$comment", "$cdata", "$pi"})


class Node:
    """Base class for active markup nodes."""

    def __init__(self, nodes, **attrs) -> None:
        self.set_content(nodes)
        self.set_attrs(attrs)

    def set_attrs(self, attrs={}) -> None:
        self._attrs = attrs

    def set_content(self, nodes) -> None:
        self._content = nodes

    def mu(self):
        raise NotImplementedError

    def xml(self) -> str:
        raise NotImplementedError


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


# Accessor functions


def tag(node):
    """The tag (node name) of the element or None."""
    return node[0] if _is_element(node) else None


def attrs(node) -> dict:
    """Dict with all attributes of the element.
    None if the node is not an element."""
    if _is_element(node):
        if has_attrs(node):
            return node[1]
        else:
            return {}
    else:
        return None


def content(node) -> list:
    if _is_element(node) and len(node) > 1:
        children = node[2:] if isinstance(node[1], dict) else node[1:]
        return [x for x in children if x is not None]
    else:
        return []


def _format_attrs(attrs: dict, mode: Mode = Mode.XML) -> str:

    output = []
    for name, value in sorted(attrs.items()):
        if value is None:
            pass
        elif isinstance(value, bool):
            if value and Mode.SGML:
                output.append(f" {name}")
            elif value:
                output.append(f' {name}="{name}"')
        elif isinstance(value, (list, tuple)):
            output.append(
                f' {name}="{util.escape_html(" ".join([str(item) for item in value]))}"'  # noqa
            )
        else:
            output.append(f' {name}="{util.escape_html(value)}"')
    return "".join(output)


def _format_special_node(node, mode: Mode = Mode.XML):
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


def _is_active_node(node) -> bool:
    return hasattr(node, "xml") and callable(getattr(node, "xml"))


def _is_active_element(node) -> bool:
    if _is_element(node):
        return _is_active_node(tag(node))
    else:
        return _is_active_node(node)


def _convert_node(node, mode: Mode = Mode.XML):

    if _is_element(node):
        yield from _convert_element(node, mode)
    elif _is_sequence(node):
        yield from _convert_sequence(node, mode)
    elif _is_active_node(node):
        yield node.xml(mode)
    else:
        yield from _convert_atomic(node, mode)


def _is_sequence(node) -> bool:
    return isinstance(node, list | tuple)


def _convert_element(node, mode: Mode = Mode.XML):
    if _is_active_element(node):
        yield from _convert_active_element(node, mode)
    elif _is_special_node(node):
        yield _format_special_node(node, mode)
    elif _is_empty_node(node):
        yield from _format_empty_node(node, mode)
    else:  # content to process
        yield from _format_content_node(node, mode)


def _format_content_node(node, mode: Mode = Mode.XML):
    node_tag = tag(node)
    node_attrs = attrs(node)
    node_attrs_xml = _format_attrs(node_attrs)
    node_content = content(node)
    yield f"<{node_tag}{node_attrs_xml}>"
    for child in node_content:
        if isinstance(child, tuple):
            for x in child:
                for y in _convert_node(x, mode):
                    yield y
        else:
            for x in _convert_node(child, mode):
                yield x
    yield f"</{node_tag}>"


def _format_empty_node(node, mode: Mode = Mode.XML):
    node_tag = tag(node)
    node_attrs = attrs(node)
    node_attrs_xml = _format_attrs(node_attrs)
    if node_tag in VOID_TAGS and mode in {Mode.HTML, Mode.XHTML}:
        yield f"<{node_tag}{node_attrs_xml}{_end_tag(mode)}"
    elif mode in {Mode.XML, Mode.SGML}:
        yield f"<{node_tag}{node_attrs_xml}{_end_tag(mode)}"
    else:
        yield f"<{node_tag}{node_attrs_xml}></{node_tag}>"


def _is_empty_node(node) -> bool:
    return len(content(node)) == 0


def _convert_active_element(node, mode: Mode = Mode.XML):
    # active element, receives attributes and content
    # and then generates xml
    node_obj = tag(node)
    node_obj.set_attrs(attrs(node))
    node_obj.set_content(content(node))
    # TODO change .xml to .markup
    yield node_obj.xml(mode)


def _convert_sequence(node, mode: Mode = Mode.XML):
    # a sequence, list would imply a malformed element
    for x in node:
        for y in _convert_node(x, mode):
            yield y


def _convert_atomic(node, mode: Mode = Mode.XML):
    # TODO: pass mode to xml() method
    if node:
        if _is_active_element(node):
            yield tag(node).xml()
        else:
            yield str(node)
    else:
        pass


# mode: html, xhtml, xml, sgml (default xml)
def _end_tag(mode):
    print(f"End tag {mode}")
    if mode == Mode.XML:
        return "/>"
    elif mode == Mode.XHTML:
        return " />"
    else:
        return ">"


def _expand_nodes(node):
    if _is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if _is_active_element(node):
            if len(node_attrs) > 0:
                node_tag.set_attrs(node_attrs)
            node_tag.set_content(node_content)
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
                rule.set_content(node_content)
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


def markup(*nodes, mode: Mode = Mode.XML):
    """Convert Mu datastructure(s) into a markup string.

    Args:
        *nodes: One or more Mu nodes to convert
        mode: Output mode, one of: "xml", "sgml", "html", "xhtml"

    Returns:
        A string containing the markup representation

    Example:
        >>> markup(["div", {"class": "content"}, "Hello"])
        '<div class="content">Hello</div>'
    """
    output = []
    for node in nodes:
        output.extend(_convert_node(node, mode))
    return "".join(output)


# experimental


def from_dict(py_value, parent=None):
    """Create a MU value from the Python value."""
    typ = type(py_value)
    if typ == int:
        return py_value
    elif py_value is None:
        return ""
    elif typ == float:
        return py_value
    elif typ == str:
        return py_value
    elif typ == bool:
        if py_value:
            return "true"
        else:
            return "false"
    elif typ == list:
        return [["li", from_dict(node)] for node in py_value]
    elif typ == dict:
        mu = ["object"] if parent is None else []
        for key in py_value:
            mu.append([key, from_dict(py_value[key], parent=key)])
        return mu
    else:
        print(f"Unhandled type: {type(py_value)}")


# syntax sugar for markup modes


def html(*nodes):
    return markup(*nodes, mode=Mode.HTML)


def xhtml(*nodes):
    return markup(*nodes, mode=Mode.XHTML)


def sgml(*nodes):
    return markup(*nodes, mode=Mode.SGML)


def xml(*nodes):
    return markup(*nodes, mode=Mode.XML)
