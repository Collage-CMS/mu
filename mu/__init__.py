#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier to
# produce XML strings.
#
#    mu.markup(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
# Conversion based on code by
# https://github.com/nbessi/pyhiccup/blob/master/pyhiccup/core.py
#
from __future__ import annotations

import mu.util as util

TREE_TYPE = list
SEQ_TYPE = tuple
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


def _is_element(value):
    return isinstance(value, TREE_TYPE) and len(value) > 0 and isinstance(value[0], str)


def _is_special_node(value):
    return _is_element(value) and value[0][0] == "$"


def _is_empty(node) -> bool:
    if len(node) == 1:
        return True
    elif len(node) == 2 and isinstance(node[1], dict):
        return True
    else:
        return False


def _has_attrs(value):
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


def attrs(node):
    """Dict with all attributes of the element.
    None if the node is not an element."""
    if _is_element(node):
        if _has_attrs(node):
            return node[1]
        else:
            return {}
    else:
        return None


def content(node):
    if _is_element(node) and len(node) > 1:
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
        elif isinstance(value, list | tuple):
            output.append(
                f' {name}="{util.escape_html(" ".join([str(item) for item in value]))}"'
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


def node_has_xml_method(node):
    return hasattr(node, "xml") and callable(getattr(node, "xml"))


def _convert_node(node, mode: str = "xml"):
    # optimization when we get a sequence of nodes
    if _is_element(node):
        node_tag = tag(node)
        node_attrs = _format_attrs(attrs(node))
        node_content = content(node)
        if _is_special_node(node):
            yield _format_special_node(node)  # TODO: add mode
        elif len(node_content) == 0:
            if node_tag in VOID_TAGS and mode in {"html", "xhtml"}:
                yield f"<{node_tag}{node_attrs}{_end_tag(mode)}"
            elif mode in {"xml", "sgml"}:
                yield f"<{node_tag}{node_attrs}{_end_tag(mode)}"
            else:
                yield f"<{node_tag}{node_attrs}></{node_tag}>"
        else:  # content to process
            yield f"<{node_tag}{node_attrs}>"
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
            if node_has_xml_method(node):
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


def markup(*nodes, mode: str = "xml"):
    """Convert a Mu datastructure into Markup string using the correct conventions."""
    output = []
    for node in nodes:
        output.extend(_convert_node(node, mode))
    return "".join(output)


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
    elif (
        typ == dict
    ):  # when inside a named node we don't need the object element only at top level
        mu = ["object"] if parent is None else []
        for key in py_value:
            mu.append([key, from_dict(py_value[key], parent=key)])
        return mu
    else:
        print(f"Unhandled type: {type(py_value)}")
