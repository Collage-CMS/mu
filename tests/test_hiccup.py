# Tests that are copied from Hiccup tests
# https://github.com/weavejester/hiccup/tree/master/test
# to ensure that Mu is compatible or that we know where it deviates
# TODO there is some overlap with the tests in test_mu.py
from __future__ import annotations

import pytest

import mu as mu

# https://github.com/weavejester/hiccup/blob/master/test/hiccup/compiler_test.clj


class TestCompile:

    def test_normal_tag_with_attrs(self):
        assert mu.markup(["p", {"id": 1}], mode="xhtml") == '<p id="1"></p>'
        assert mu.markup(["p", {"id": 1}], mode="html") == '<p id="1"></p>'
        assert mu.markup(["p", {"id": 1}], mode="xml") == '<p id="1"/>'
        assert mu.markup(["p", {"id": 1}], mode="sgml") == '<p id="1">'

    def test_void_tag_with_attrs(self):
        assert mu.markup(["br", {"id": 1}], mode="xhtml") == '<br id="1" />'
        assert mu.markup(["br", {"id": 1}], mode="html") == '<br id="1">'
        assert mu.markup(["br", {"id": 1}], mode="xml") == '<br id="1"/>'
        assert mu.markup(["br", {"id": 1}], mode="sgml") == '<br id="1">'

    def test_normal_tag_with_content(self):
        assert mu.markup(["p", "x"], mode="xhtml") == "<p>x</p>"
        assert mu.markup(["p", "x"], mode="html") == "<p>x</p>"
        assert mu.markup(["p", "x"], mode="xml") == "<p>x</p>"
        assert mu.markup(["p", "x"], mode="sgml") == "<p>x</p>"

    def test_void_tag_with_content(self):
        assert mu.markup(["br", "x"], mode="xhtml") == "<br>x</br>"
        assert mu.markup(["br", "x"], mode="html") == "<br>x</br>"
        assert mu.markup(["br", "x"], mode="xml") == "<br>x</br>"
        assert mu.markup(["br", "x"], mode="sgml") == "<br>x</br>"

    def test_normal_tag_without_attrs(self):
        assert mu.markup(["p", {}], mode="xhtml") == "<p></p>"
        assert mu.markup(["p", {}], mode="html") == "<p></p>"
        assert mu.markup(["p", {}], mode="xml") == "<p/>"
        assert mu.markup(["p", {}], mode="sgml") == "<p>"
        assert mu.markup(["p", None], mode="xhtml") == "<p></p>"
        assert mu.markup(["p", None], mode="html") == "<p></p>"
        assert mu.markup(["p", None], mode="xml") == "<p/>"
        assert mu.markup(["p", None], mode="sgml") == "<p>"

    def test_void_tag_without_attrs(self):
        assert mu.markup(["br", {}], mode="xhtml") == "<br />"
        assert mu.markup(["br", {}], mode="html") == "<br>"
        assert mu.markup(["br", {}], mode="xml") == "<br/>"
        assert mu.markup(["br", {}], mode="sgml") == "<br>"
        assert mu.markup(["br", None], mode="xhtml") == "<br />"
        assert mu.markup(["br", None], mode="html") == "<br>"
        assert mu.markup(["br", None], mode="xml") == "<br/>"
        assert mu.markup(["br", None], mode="sgml") == "<br>"


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
        assert mu.markup(["div"], mode="xhtml") == "<div></div>"
        assert mu.markup(["h1"]) == "<h1/>"
        assert mu.markup(["h1"], mode="xhtml") == "<h1></h1>"
        assert mu.markup(["script"]) == "<script/>"
        assert mu.markup(["script"], mode="xhtml") == "<script></script>"
        assert mu.markup(["text"]) == "<text/>"
        assert mu.markup(["text"], mode="xhtml") == "<text></text>"
        assert mu.markup(["a"]) == "<a/>"
        assert mu.markup(["a"], mode="xhtml") == "<a></a>"
        assert mu.markup(["iframe"]) == "<iframe/>"
        assert mu.markup(["iframe"], mode="xhtml") == "<iframe></iframe>"
        assert mu.markup(["title"]) == "<title/>"
        assert mu.markup(["title"], mode="xhtml") == "<title></title>"
        assert mu.markup(["section"]) == "<section/>"
        assert mu.markup(["section"], mode="xhtml") == "<section></section>"
        assert mu.markup(["select"]) == "<select/>"
        assert mu.markup(["select"], mode="xhtml") == "<select></select>"
        assert mu.markup(["object"]) == "<object/>"
        assert mu.markup(["object"], mode="xhtml") == "<object></object>"
        assert mu.markup(["video"]) == "<video/>"
        assert mu.markup(["video"], mode="xhtml") == "<video></video>"

    def test_void_tags(self):
        assert mu.markup(["br"]) == "<br/>"
        assert mu.markup(["br"], mode="xhtml") == "<br />"
        assert mu.markup(["link"]) == "<link/>"
        assert mu.markup(["link"], mode="xhtml") == "<link />"
        assert mu.markup(["colgroup", {"span": 2}]) == '<colgroup span="2"/>'
        assert (
            mu.markup(["colgroup", {"span": 2}], mode="xhtml")
            == '<colgroup span="2"></colgroup>'
        )

    def test_containing_text(self):
        assert mu.markup(["text", "Lorem Ipsum"]) == "<text>Lorem Ipsum</text>"

    def test_contents_are_concatenated(self):
        assert mu.markup(["body", "foo", "bar"]) == "<body>foobar</body>"
        assert mu.markup(["body", ["p"], ["br"]]) == "<body><p/><br/></body>"
        # FIXME
        # assert (
        #    mu.markup(["body", ["p"], ["br"]], mode="xhtml")
        #    == "<body><p></p><br /></body>"
        # )

    def test_seqs_are_expanded(self):
        # FIXME
        # assert mu.markup(([["p", "a"],["p", "b"]])) == "<p>a</p><p>b</p>"
        pass

    def test_tags_can_contain_tags(self):
        assert mu.markup(["div", ["p"]]) == "<div><p/></div>"
        # FIXME
        # assert mu.markup(["div", ["p"]], mode="xhtml") == "<div><p></p></div>"


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
            mu.markup(["input", {"type": "checkbox", "checked": True}], mode="html")
            == '<input checked="checked" type="checkbox">'
        )
        assert (
            mu.markup(["input", {"type": "checkbox", "checked": False}], mode="html")
            == '<input type="checkbox">'
        )

    def test_nil_attributes(self):
        assert mu.markup(["span", {"class": None}]) == "<span/>"

    def test_tag_with_vector_class(self):
        # TODO tests for syntactic sugar on element names
        pass


class TestRenderModes:

    def test_closed_tag(self):
        assert mu.markup(["p"], ["br"]) == "<p/><br/>"
        assert mu.markup(["p"], ["br"], mode="xhtml") == "<p></p><br />"
        assert mu.markup(["p"], ["br"], mode="html") == "<p></p><br>"
        assert mu.markup(["p"], ["br"], mode="xml") == "<p/><br/>"
        assert mu.markup(["p"], ["br"], mode="sgml") == "<p><br>"

    @pytest.mark.skip(reason="this functionality is not yet implemented")
    def test_boolean_attributes(self):
        assert (
            mu.markup(["input", {"type": "checkbox", "checked": True}])
            == '<input checked="checked" type="checkbox"/>'
        )
        assert (
            mu.markup(["input", {"type": "checkbox", "checked": True}], mode="sgml")
            == '<input checked type="checkbox">'
        )
