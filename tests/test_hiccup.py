# Tests that are copied from Hiccup tests
# https://github.com/weavejester/hiccup/tree/master/test
# to ensure that Mu is compatible or that we know where it deviates
# TODO there is some overlap with the tests in test_mu.py
from __future__ import annotations

import mu as mu

# https://github.com/weavejester/hiccup/blob/master/test/hiccup/compiler_test.clj


class TestCompile:

    def test_normal_tag_with_attrs(self):
        assert mu.markup(["p", {"id": 1}], mode=mu.Mode.XHTML) == '<p id="1"></p>'
        assert mu.markup(["p", {"id": 1}], mode=mu.Mode.HTML) == '<p id="1"></p>'
        assert mu.markup(["p", {"id": 1}], mode=mu.Mode.XML) == '<p id="1"/>'
        assert mu.markup(["p", {"id": 1}], mode=mu.Mode.SGML) == '<p id="1">'

    def test_void_tag_with_attrs(self):
        assert mu.markup(["br", {"id": 1}], mode=mu.Mode.XHTML) == '<br id="1" />'
        assert mu.markup(["br", {"id": 1}], mode=mu.Mode.HTML) == '<br id="1">'
        assert mu.markup(["br", {"id": 1}], mode=mu.Mode.XML) == '<br id="1"/>'
        assert mu.markup(["br", {"id": 1}], mode=mu.Mode.SGML) == '<br id="1">'

    def test_normal_tag_with_content(self):
        assert mu.markup(["p", "x"], mode=mu.Mode.XHTML) == "<p>x</p>"
        assert mu.markup(["p", "x"], mode=mu.Mode.HTML) == "<p>x</p>"
        assert mu.markup(["p", "x"], mode=mu.Mode.XML) == "<p>x</p>"
        assert mu.markup(["p", "x"], mode=mu.Mode.SGML) == "<p>x</p>"

    def test_void_tag_with_content(self):
        assert mu.markup(["br", "x"], mode=mu.Mode.XHTML) == "<br>x</br>"
        assert mu.markup(["br", "x"], mode=mu.Mode.HTML) == "<br>x</br>"
        assert mu.markup(["br", "x"], mode=mu.Mode.XML) == "<br>x</br>"
        assert mu.markup(["br", "x"], mode=mu.Mode.SGML) == "<br>x</br>"

    def test_normal_tag_without_attrs(self):
        assert mu.markup(["p", {}], mode=mu.Mode.XHTML) == "<p></p>"
        assert mu.markup(["p", {}], mode=mu.Mode.HTML) == "<p></p>"
        assert mu.markup(["p", {}], mode=mu.Mode.XML) == "<p/>"
        assert mu.markup(["p", {}], mode=mu.Mode.SGML) == "<p>"
        assert mu.markup(["p", None], mode=mu.Mode.XHTML) == "<p></p>"
        assert mu.markup(["p", None], mode=mu.Mode.HTML) == "<p></p>"
        assert mu.markup(["p", None], mode=mu.Mode.XML) == "<p/>"
        assert mu.markup(["p", None], mode=mu.Mode.SGML) == "<p>"

    def test_void_tag_without_attrs(self):
        assert mu.markup(["br", {}], mode=mu.Mode.XHTML) == "<br />"
        assert mu.markup(["br", {}], mode=mu.Mode.HTML) == "<br>"
        assert mu.markup(["br", {}], mode=mu.Mode.XML) == "<br/>"
        assert mu.markup(["br", {}], mode=mu.Mode.SGML) == "<br>"
        assert mu.markup(["br", None], mode=mu.Mode.XHTML) == "<br />"
        assert mu.markup(["br", None], mode=mu.Mode.HTML) == "<br>"
        assert mu.markup(["br", None], mode=mu.Mode.XML) == "<br/>"
        assert mu.markup(["br", None], mode=mu.Mode.SGML) == "<br>"


# https://github.com/weavejester/hiccup/blob/master/test/hiccup/core_test.clj


class TestTagNames:

    def basic_tags(self):
        assert mu.markup(["div"]) == "<div></div>"

    # def tag_syntactic_sugar(self):
    #     pass


class TestTagContents:

    def test_empty_tags(self):
        # NOTE default mode is XML, hiccup's default mode is XHTML
        assert mu.markup(["div"]) == "<div/>"
        assert mu.markup(["div"], mode=mu.Mode.XHTML) == "<div></div>"
        assert mu.markup(["h1"]) == "<h1/>"
        assert mu.markup(["h1"], mode=mu.Mode.XHTML) == "<h1></h1>"
        assert mu.markup(["script"]) == "<script/>"
        assert mu.markup(["script"], mode=mu.Mode.XHTML) == "<script></script>"
        assert mu.markup(["text"]) == "<text/>"
        assert mu.markup(["text"], mode=mu.Mode.XHTML) == "<text></text>"
        assert mu.markup(["a"]) == "<a/>"
        assert mu.markup(["a"], mode=mu.Mode.XHTML) == "<a></a>"
        assert mu.markup(["iframe"]) == "<iframe/>"
        assert mu.markup(["iframe"], mode=mu.Mode.XHTML) == "<iframe></iframe>"
        assert mu.markup(["title"]) == "<title/>"
        assert mu.markup(["title"], mode=mu.Mode.XHTML) == "<title></title>"
        assert mu.markup(["section"]) == "<section/>"
        assert mu.markup(["section"], mode=mu.Mode.XHTML) == "<section></section>"
        assert mu.markup(["select"]) == "<select/>"
        assert mu.markup(["select"], mode=mu.Mode.XHTML) == "<select></select>"
        assert mu.markup(["object"]) == "<object/>"
        assert mu.markup(["object"], mode=mu.Mode.XHTML) == "<object></object>"
        assert mu.markup(["video"]) == "<video/>"
        assert mu.markup(["video"], mode=mu.Mode.XHTML) == "<video></video>"

    def test_void_tags(self):
        assert mu.markup(["br"]) == "<br/>"
        assert mu.markup(["br"], mode=mu.Mode.XHTML) == "<br />"
        assert mu.markup(["link"]) == "<link/>"
        assert mu.markup(["link"], mode=mu.Mode.XHTML) == "<link />"
        assert mu.markup(["colgroup", {"span": 2}]) == '<colgroup span="2"/>'
        assert (
            mu.markup(["colgroup", {"span": 2}], mode=mu.Mode.XHTML)
            == '<colgroup span="2"></colgroup>'
        )

    def test_containing_text(self):
        assert mu.markup(["text", "Lorem Ipsum"]) == "<text>Lorem Ipsum</text>"

    def test_contents_are_concatenated(self):
        assert mu.markup(["body", "foo", "bar"]) == "<body>foobar</body>"
        assert mu.markup(["body", ["p"], ["br"]]) == "<body><p/><br/></body>"
        # FIXME
        # assert (
        #    mu.markup(["body", ["p"], ["br"]], mode=mu.Mode.XHTML)
        #    == "<body><p></p><br /></body>"
        # )

    def test_seqs_are_expanded(self):
        # FIXME
        # assert mu.markup(([["p", "a"],["p", "b"]])) == "<p>a</p><p>b</p>"
        pass

    def test_tags_can_contain_tags(self):
        assert mu.markup(["div", ["p"]]) == "<div><p/></div>"
        # FIXME
        # assert mu.markup(["div", ["p"]], mode=mu.Mode.XHTML) == "<div><p></p></div>"


class TestTagAttributes:

    def test_tag_with_blank_attribute_map(self):
        assert mu.markup(["xml", {}]) == "<xml/>"
        assert mu.markup(["xml", None]) == "<xml/>"

    def test_tag_with_populated_attribute_map(self):
        assert mu.markup(["xml", {"a": 123}]) == '<xml a="123"/>'
        assert (
            mu.markup(["xml", {"a": 1, "b": 2, "c": 3}]) == '<xml a="1" b="2" c="3"/>'
        )
        assert mu.markup(["img", {"id": 1}]) == '<img id="1"/>'
        # how to render this?
        assert mu.markup(["xml", {"a": ["kw", "foo", 3]}]) == '<xml a="kw foo 3"/>'

    def test_attribute_values_are_escaped(self):
        assert mu.markup(["div", {"id": "<>&"}]) == '<div id="&lt;&gt;&amp;"/>'

    def test_boolean_attributes(self):
        assert (
            mu.html(["input", {"type": "checkbox", "checked": True}])
            == '<input checked type="checkbox">'
        )
        assert (
            mu.html(["input", {"type": "checkbox", "checked": False}])
            == '<input type="checkbox">'
        )

    def test_nil_attributes(self):
        assert mu.markup(["span", {"class": None}]) == "<span/>"

    def test_tag_with_vector_class(self):
        # TODO tests for syntactic sugar on element names
        pass


class TestRenderModes:

    def test_closed_tag(self):
        assert mu.markup(["p"], ["br"]) == "<p/><br/>"  # default mode = xml
        assert mu.xhtml(["p"], ["br"]) == "<p></p><br />"
        assert mu.html(["p"], ["br"]) == "<p></p><br>"
        assert mu.xml(["p"], ["br"]) == "<p/><br/>"
        assert mu.sgml(["p"], ["br"]) == "<p><br>"
