#
# Generate XML using a regular Python data structure.
#
# Note that this does not guarantee well-formed XML but it does make it easier to
# produce XML strings.
#
#    mu.parse(['foo', {'a': 10}, 'bar']) => <foo a="10">bar</foo>
#
# TODO Needs much more checking on valid QNames, illegal constructs etc.
# TODO Add functions to manipulate Mu structures.
# TODO Add namespaces and generate well-formed XML (or auto-gen at top)
# Predicates
from __future__ import annotations


def _is_element(value):
    if isinstance(value, list) and len(value) > 0 and isinstance(value[0], str):
        return True
    else:
        return False


def _is_special_node(value):
    if _is_element(value) and value[0][0] == "$":
        return True
    else:
        return False


def _has_attrs(value):
    if (
        _is_element(value)
        and len(value) > 1
        and type(value[1]) is dict
        and len(value[1]) > 0
    ):
        return True
    else:
        return False


# Accessor functions


def _tag(value):
    if _is_element(value):
        return value[0]
    else:
        return None


def _attrs(value):
    if _has_attrs(value):
        return value[1]
    else:
        return {}


# Serialization functions


def _mu_attrs(attrs):
    attrlist = []
    for key in attrs:
        attrlist.append(f'{key}="{attrs[key]}"')
    return " ".join(attrlist)


def _mu_special_node(value):
    if _tag(value) == "$comment":
        return "<!-- " + "".join(value[1:]) + " -->"
    elif _tag(value) == "$cdata":
        return "<![CDATA[" + "".join(value[1:]) + "]]>"
    elif _tag(value) == "$pi":
        return "<?" + "".join(value[1:]) + "?>"
    else:
        # Silently swallow elements that start with $...
        return ""


def _mu_element_node(value):
    xml = ""
    tag = _tag(value)
    attrs = _attrs(value)
    content = []
    if len(value) > 1 and type(value[1]) is not dict:
        content = value[1:]
    elif len(value) > 2:
        content = value[2:]
    xml += f"<{tag}"
    if len(attrs) > 0:
        xml += f" { _mu_attrs(attrs)}"
    if len(content) > 0:
        xml += ">"
        for node in content:
            xml += _mu_xml(node)
        xml += f"</{tag}>"
    else:
        xml += "/>"
    return xml


def _mu_xml(value):
    if _is_element(value):
        if _is_special_node(value):
            return _mu_special_node(value)
        else:
            return _mu_element_node(value)
    else:
        return str(value)


def xml(mu):
    """Convert a Mu datastructure into an XML formatted string."""
    return _mu_xml(mu)


def xslt(*mu, version=3.0):
    """Wrap a mu document in  XSLT wrapper"""
    wrapper = [
        "xsl:stylesheet",
        {"version": version, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
    ]
    return wrap(wrapper, *mu)


def svg(*mu, version=3.0):
    """Wrap a mu document in SVG wrapper"""
    return wrap(["svg", {"xmlns": "http://www.w3.org/2000/svg"}], *mu)


def wrap(nodes=[], *mu):
    """Wrap XML"""
    for node in mu:
        nodes.append(node)
    return nodes
