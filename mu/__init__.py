#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier
# to produce XML strings.
#
#    mu.markup(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
from __future__ import annotations

import mu.util as util

VOID_TAGS = {
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


class Node:

    def __init__(self, node, **attrs):
        self._content = node
        self._attrs = attrs

    def set_attrs(self, attrs: dict = {}):
        self._attrs = attrs

    def set_content(self, node):
        self._content = node

    def mu(self):
        pass

    def xml(self):
        pass


def is_element(value):
    return (
        isinstance(value, list) and len(value) > 0 and isinstance(value[0], (str, Node))
    )


def is_special_node(value):
    return is_element(value) and isinstance(value[0], str) and value[0][0] == "$"


def is_empty(node) -> bool:
    if len(node) == 1:
        return True
    elif len(node) == 2 and isinstance(node[1], dict):
        return True
    else:
        return False


def has_attrs(value):
    return (
        is_element(value)
        and len(value) > 1
        and isinstance(value[1], dict)
        and len(value[1]) > 0
    )


# Accessor functions


def tag(node):
    """The tag (node name) of the element or None."""
    return node[0] if is_element(node) else None


def attrs(node):
    """Dict with all attributes of the element.
    None if the node is not an element."""
    if is_element(node):
        if has_attrs(node):
            return node[1]
        else:
            return {}
    else:
        return None


def content(node) -> list:
    if is_element(node) and len(node) > 1:
        children = node[2:] if isinstance(node[1], dict) else node[1:]
        return [x for x in children if x is not None]
    else:
        return []


def _format_attrs(attributes, mode: str = "xml"):
    output = []
    for name, value in sorted(attributes.items()):
        if value is None:
            pass
        elif isinstance(value, bool):
            if value and mode == "sgml":
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


def _format_special_node(value):
    if tag(value) == "$raw":
        return "".join(value[1:])
    elif tag(value) == "$comment":
        return f'<!-- {"".join(value[1:])} -->'
    elif tag(value) == "$cdata":
        return f'<![CDATA[{"".join(value[1:])}]]>'
    elif tag(value) == "$pi":
        return f'<?{"".join(value[1:])}?>'
    else:
        return ""


def _node_has_xml_method(node):
    return hasattr(node, "xml") and callable(getattr(node, "xml"))


def _node_has_mu_method(node):
    return hasattr(node, "xml") and callable(getattr(node, "xml"))


def _convert_node(node, mode: str = "xml"):
    if is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_attrs_xml = _format_attrs(node_attrs)
        node_content = content(node)
        if _node_has_xml_method(node_tag):
            # active element, receives attributes and content
            # and then generates xml
            node_tag.set_attrs(node_attrs)
            node_tag.set_content(node_content)
            yield node_tag.xml()
        elif is_special_node(node):
            yield _format_special_node(node)
        elif len(node_content) == 0:
            if node_tag in VOID_TAGS and mode in {"html", "xhtml"}:
                yield f"<{node_tag}{node_attrs_xml}{_end_tag(mode)}"
            elif mode in {"xml", "sgml"}:
                yield f"<{node_tag}{node_attrs_xml}{_end_tag(mode)}"
            else:
                yield f"<{node_tag}{node_attrs_xml}></{node_tag}>"
        else:  # content to process
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
    elif isinstance(node, list | tuple):
        # a sequence, list would imply a malformed element
        for x in node:
            for y in _convert_node(x, mode):
                yield y
    else:  # atomic value
        if node:
            if _node_has_xml_method(node):
                yield node.xml()
            else:
                yield str(node)
        else:
            pass


# mode: html, xhtml, xml, sgml (default xml)
def _end_tag(mode):
    if mode == "xml":
        return "/>"
    elif mode == "xhtml":
        return " />"
    else:
        return ">"


def _expand_node(node):
    if is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if _node_has_mu_method(node_tag):
            if len(node_attrs) > 0:
                node_tag.set_attrs(node_attrs)
            node_tag.set_content(node_content)
            return node_tag.mu()
        else:
            mu = [node_tag]
            if len(node_attrs) > 0:
                mu.append(node_attrs)
            mu.extend([_expand_node(child) for child in node_content])
            return mu
    elif isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_expand_node(child))
        return mu
    else:
        if _node_has_mu_method(node):
            return node.mu()
        else:
            return node


def _apply_node(node, rules: dict):
    if is_element(node):
        node_tag = tag(node)
        node_attrs = attrs(node)
        node_content = content(node)
        if node_tag in rules:
            if _node_has_mu_method(rules[node_tag]):
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
            mu.extend([_apply_node(child, rules) for child in node_content])
            return mu
    elif isinstance(node, (list, tuple)):
        mu = []
        for child in node:
            if child is not None:
                mu.append(_apply_node(child, rules))
        return mu
    else:
        return node


def expand(nodes):
    """Expand a Mu datastructure (invoking all Mu objects mu() method)."""
    return _expand_node(nodes)


def apply(nodes, rules: dict):
    """Expand a Mu datastructure replacing nodes that have a rule by invoking
    its value mu() method."""
    return _apply_node(nodes, rules)


def markup(*nodes, mode: str = "xml"):
    """Convert a Mu datastructure into Markup string using the correct
    conventions."""
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
