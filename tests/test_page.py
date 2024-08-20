from __future__ import annotations

import pytest

import mu.page as page


class TestXMLDeclaration:

    def test_xml_declaration(self):
        assert page.xml_declaration("UTF-8") == [
            "$raw",
            '<?xml version="1.0" encoding="UTF-8"?>\n',
        ]


class TestPageWrappers:

    def test_xslt_wrapper(self):
        result = [
            "xsl:stylesheet",
            {"version": 3.0, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
            ["xsl:template"],
        ]
        assert page.xslt(["xsl:template"]) == result

    def test_xslt_wrapper_with_attrs(self):
        result = [
            "xsl:stylesheet",
            {
                "version": 3.0,
                "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform",
                "x": 10,
            },
            ["xsl:template"],
        ]
        assert page.xslt(["xsl:template"], attrs={"x": 10}) == result

    def test_svg_wrapper(self):
        result = ["svg", {"xmlns": "http://www.w3.org/2000/svg"}, ["rect"]]
        assert page.svg(["rect"]) == result

    def test_svg_wrapper_with_attrs(self):
        result = ["svg", {"xmlns": "http://www.w3.org/2000/svg", "x": 10}, ["rect"]]
        assert page.svg(["rect"], attrs={"x": 10}) == result


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/page_test.clj


class TestHTML4:

    def test_html4(self):
        assert (
            page.html4(["body", ["p", "Hello", ["br"], "World"]])
            == '<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN" '
            '"http://www.w3.org/TR/html4/strict.dtd">\n'
            "<html><body><p>Hello<br>World</p></body></html>"
        )


class TestXHTML:

    def test_xhtml(self):
        assert (
            page.xhtml(["body", ["p", "Hello", ["br"], "World"]])
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">'
            "<body><p>Hello<br />World</p></body></html>"
        )

    def test_xhtml_with_language(self):
        assert (
            page.xhtml(["body", "Hello World"], lang="en")
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
            '<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">'
            "<body>Hello World</body></html>"
        )

    def test_xhtml_with_encoding(self):
        assert (
            page.xhtml(["body", "Hello World"], encoding="ISO-8859-1")
            == '<?xml version="1.0" encoding="ISO-8859-1"?>\n'
            '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" '
            '"http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">\n'
            '<html xmlns="http://www.w3.org/1999/xhtml">'
            "<body>Hello World</body></html>"
        )


class TestHTML5:

    @pytest.mark.skip(reason="not fully implemented yet")
    def test_html_mode(self):
        assert (
            page.html5(["body", ["p", "Hello", ["br"], "World"]])
            == "<!DOCTYPE html>\n<html><body><p>Hello<br>World</p></body></html>"
        )
        assert (
            page.html5({"lang": "en"}, ["body", "Hello World"])
            == '<!DOCTYPE html>\n<html lang="en"><body>Hello World</body></html>'
        )
        assert (
            page.html5({"prefix": "og: http://ogp.me/ns#"}, ["body", "Hello World"])
            == "<!DOCTYPE html>\n"
            '<html prefix="og: http://ogp.me/ns#">'
            "<body>Hello World</body></html>"
        )
        assert (
            page.html5(
                {"prefix": "og: http://ogp.me/ns#", "lang": "en"},
                ["body", "Hello World"],
            )
            == "<!DOCTYPE html>\n"
            '<html lang="en" prefix="og: http://ogp.me/ns#">'
            "<body>Hello World</body></html>"
        )

    # FIXME don't know what to do with pseudo attribute :xml? in Hiccup example

    def test_xhtml_mode(self):
        assert (
            page.html5(["body", ["p", "Hello", ["br"], "World"]], mode="xhtml")
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            '<!DOCTYPE html>\n<html xmlns="http://www.w3.org/1999/xhtml">'
            "<body><p>Hello<br />World</p></body></html>"
        )
        assert (
            page.html5(["body", "Hello World"], lang="en", mode="xhtml")
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!DOCTYPE html>\n"
            '<html lang="en" xml:lang="en" xmlns="http://www.w3.org/1999/xhtml">'
            "<body>Hello World</body></html>"
        )
        assert (
            page.html5(
                ["body", "Hello World"],
                attrs={"xml:og": "http://ogp.me/ns#"},
                mode="xhtml",
            )
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!DOCTYPE html>\n"
            '<html xml:og="http://ogp.me/ns#" xmlns="http://www.w3.org/1999/xhtml">'
            "<body>Hello World</body></html>"
        )
        assert (
            page.html5(
                ["body", "Hello World"],
                attrs={"lang": "en", "xml:og": "http://ogp.me/ns#"},
                mode="xhtml",
            )
            == '<?xml version="1.0" encoding="UTF-8"?>\n'
            "<!DOCTYPE html>\n"
            '<html lang="en" xml:og="http://ogp.me/ns#"'
            ' xmlns="http://www.w3.org/1999/xhtml">'
            "<body>Hello World</body></html>"
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
