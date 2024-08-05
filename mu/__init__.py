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

TREE_TYPE = (list, tuple)
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
    return isinstance(value, list) and len(value) > 0 and isinstance(value[0], str)


def _is_special_node(value):
    return _is_element(value) and value[0][0] == "$"


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
        return node[2:] if isinstance(node[1], dict) else node[1:]
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


def _convert_node(node, mode: str = "xml"):
    # optimization when we get a sequence of nodes
    if isinstance(node[0], TREE_TYPE):
        for sub_node in node:
            for x in _convert_node(sub_node, mode):
                yield x
    if _is_special_node(node):
        yield _format_special_node(node)
    else:
        node_tag = node[0]
        rest = node[1:] if len(node) > 1 else []
        node_attrs = ""
        node_children = []
        for element in rest:
            if not element:
                continue
            elif isinstance(element, TREE_TYPE):
                if isinstance(element[0], TREE_TYPE):
                    node_children.extend(element)
                else:
                    node_children.append(element)
            elif isinstance(element, dict):
                node_attrs = _format_attrs(element, mode)
            else:
                node_children.append(element)
        if node_children:
            yield f"<{node_tag}{node_attrs}>"
            for ext in node_children:
                if isinstance(ext, TREE_TYPE):
                    for x in _convert_node(ext, mode):
                        yield x
                else:
                    yield util.escape_html(ext)
            yield f"</{node_tag}>"
        else:
            if node_tag in VOID_TAGS and mode in {"html", "xhtml"}:
                yield f"<{node_tag}{node_attrs}{_end_tag(mode)}"
            elif mode in {"xml", "sgml"}:
                yield f"<{node_tag}{node_attrs}{_end_tag(mode)}"
            else:
                yield f"<{node_tag}{node_attrs}></{node_tag}>"


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
