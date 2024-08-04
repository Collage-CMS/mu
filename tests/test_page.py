from __future__ import annotations

import mu.page as page


class TestPage:

    def test_html4(self):
        assert page.html4(
            ["head", ["title", "Foobar"]], ["body", ["p", "Hello", ["br"], "World"]]
        ) == "".join(
            [
                '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" "http://www.w3.org/TR/html4/strict.dtd">\n'  # noqa: E501
                "<html><head><title>Foobar</title></head><body><p>Hello<br>World</p></body></html>"  # noqa: E501
            ]
        )


class TestIncludeJs:

    def test_include_js(self):
        assert page.include_js("foo.js") == [
            ["script", {"src": "foo.js", "type": "text/javascript"}]
        ]
        assert page.include_js("foo.js", "bar.js") == [
            ["script", {"src": "foo.js", "type": "text/javascript"}],
            ["script", {"src": "bar.js", "type": "text/javascript"}],
        ]


class TestIncludeCss:

    def test_include_css(self):
        assert page.include_css("foo.css") == [
            ["link", {"type": "text/css", "href": "foo.css", "rel": "stylesheet"}]
        ]
        assert page.include_css("foo.css", "bar.css") == [
            ["link", {"type": "text/css", "href": "foo.css", "rel": "stylesheet"}],
            ["link", {"type": "text/css", "href": "bar.css", "rel": "stylesheet"}],
        ]


class TestPageWrappers:

    def test_xslt_wrapper(self):
        result = [
            "xsl:stylesheet",
            {"version": 3.0, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
            ["xsl:template"],
        ]
        assert page.xslt(["xsl:template"]) == result

    def test_svg_wrapper(self):
        result = ["svg", {"xmlns": "http://www.w3.org/2000/svg"}, ["rect"]]
        assert page.svg(["rect"]) == result
