from __future__ import annotations

import mu as mu
from mu.util import raw_string


doctype = {
    "html4": raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'  # noqa: E501
    ),
    "xhtml-strict": raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'  # noqa: E501
    ),
    "xhtml-transitional": raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'  # noqa: E501
    ),
    "html5": raw_string("<!DOCTYPE html>\n"),
}


def xml_declaration(encoding):
    return raw_string(f'<?xml version="1.0" encoding="{encoding}"?>\n')


def html4(*contents):
    return mu.markup(doctype["html4"], ["html", *contents], mode="sgml")


def html5(*contents):
    return mu.markup(["html", *contents])


def xhtml(*contents):
    return mu.markup(doctype["xhtml-strict"], ["html", *contents], mode="xhtml")


def script_element(src):
    return ["script", {"type": "text/javascript", "src": src}]


def style_element(src):
    return ["link", {"type": "text/css", "href": src, "rel": "stylesheet"}]


def include_js(*scripts):
    return [script_element(node) for node in scripts]


def include_css(*styles):
    return [style_element(node) for node in styles]


def xslt(*nodes, version=3.0):
    """Wrap a mu document in  XSLT wrapper"""
    wrapper = [
        "xsl:stylesheet",
        {"version": version, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
    ]
    return mu.wrap(wrapper, *nodes)


def svg(*nodes, version=3.0):
    """Wrap a mu document in SVG wrapper"""
    return mu.wrap(["svg", {"xmlns": "http://www.w3.org/2000/svg"}], *nodes)
