from __future__ import annotations

import mu as mu
import mu.element as el
import mu.util as util


doctype = {
    "html4": util.raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'  # noqa: E501
    ),
    "xhtml-strict": util.raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'  # noqa: E501
    ),
    "xhtml-transitional": util.raw_string(
        '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">\n'  # noqa: E501
    ),
    "html5": util.raw_string("<!DOCTYPE html>\n"),
}


def xml_declaration(encoding):
    return util.raw_string(f'<?xml version="1.0" encoding="{encoding}"?>\n')


def html4(*contents, attrs: dict = {}):
    wrapper = ["html4"]
    wrapper.append(attrs) if attrs else wrapper
    return mu.markup(doctype["html4"], el.wrap(["html"], contents), mode="sgml")


def html5(
    *contents,
    lang: str = None,
    encoding: str = "UTF-8",
    attrs: dict = {},
    mode: str = "html",
):
    html_attrs = attrs
    html_attrs["xmlns"] = (
        "http://www.w3.org/1999/xhtml" if mode == "xhtml" else html_attrs
    )
    if lang:
        html_attrs["lang"] = lang
        html_attrs["xml:lang"] = lang
    wrapper = ["html"]
    wrapper.append(html_attrs) if html_attrs else wrapper
    if mode == "xhtml":
        return mu.markup(
            xml_declaration(encoding),
            doctype["html5"],
            el.wrap(wrapper, contents),
            mode="xhtml",
        )
    else:
        return mu.markup(doctype["html5"], ["html", {}, *contents], mode="html")


def xhtml(*contents, lang: str = None, encoding: str = "UTF-8", attrs: dict = {}):
    html_attrs = {"xmlns": "http://www.w3.org/1999/xhtml"}
    if lang:
        html_attrs["lang"] = lang
        html_attrs["xml:lang"] = lang
    wrapper = ["html", html_attrs]
    return mu.markup(
        xml_declaration(encoding),
        doctype["xhtml-strict"],
        el.wrap(wrapper, contents),
        mode="xhtml",
    )


def script_element(src):
    return ["script", {"type": "text/javascript", "src": src}]


def style_element(src):
    return ["link", {"type": "text/css", "href": src, "rel": "stylesheet"}]


def include_js(*scripts):
    return [script_element(node) for node in scripts]


def include_css(*styles):
    return [style_element(node) for node in styles]


def xslt(*nodes, version=3.0, attrs: dict = {}):
    """Wrap a mu document in  XSLT wrapper"""
    wrapper = [
        "xsl:stylesheet",
        attrs
        | {"version": version, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
    ]
    return el.wrap(wrapper, nodes)


def svg(*nodes, attrs: dict = {}):
    """Wrap a mu document in SVG wrapper"""
    wrapper = ["svg", attrs | {"xmlns": "http://www.w3.org/2000/svg"}]
    return el.wrap(wrapper, nodes)
