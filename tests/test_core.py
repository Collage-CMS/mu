from __future__ import annotations

import pytest

import mu

# TODO Add functions to manipulate Mu structures.
# TODO Add namespaces and generate well-formed XML (or auto-gen at top)


class OL(mu.Node):

    def __init__(self, *items):
        self._content = list(items)
        self._attrs = {}

    def mu(self):
        ol = ["ol"]
        if len(self._attrs) > 0:
            ol.append(self._attrs)
        for item in self._content:
            ol.append(["li", item])
        return ol

    def xml(self):
        return mu.markup(self.mu())


class TestAccessors:

    def test_tag(self):
        assert mu.tag(["foo"]) == "foo"
        assert mu.tag(["$foo"]) == "$foo"
        assert mu.tag(None) is None
        assert mu.tag(0) is None
        assert mu.tag([]) is None
        assert mu.tag({}) is None

    def test_no_attrs(self):
        assert mu.attrs(["foo"]) == {}
        assert mu.attrs(["foo", {}]) == {}
        assert mu.attrs(["foo", "bla", {"a": 10}]) == {}

    def test_attrs(self):
        assert mu.attrs(["foo", {"a": 10, "b": 20}]) == {"a": 10, "b": 20}

    def test_content(self):
        assert mu.content(["foo", "bar", "baz"]) == ["bar", "baz"]
        assert mu.content(["foo"]) == []
        assert mu.content(["foo", {}]) == []
        assert mu.content(["foo", "bar"]) == ["bar"]


class TestIsElement:

    def test_is_not_element(self):
        assert mu._is_element([]) is False
        assert mu._is_element(0) is False
        assert mu._is_element(None) is False
        assert mu._is_element({}) is False
        assert mu._is_element("foo") is False
        assert mu._is_element(True) is False

    def test_is_element(self):
        assert mu._is_element(["foo"]) is True
        assert mu._is_element(["foo", ["bar"]]) is True
        assert mu._is_element(["foo", "bla"]) is True
        assert mu._is_element(["foo", {}, "bla"]) is True

    def test_is_not_active_element(self):
        assert mu._is_active_element([bool, 1, 2, 3]) is False

    def test_is_active_element(self):
        assert mu._is_element([OL(), 1, 2, 3]) is True
        assert mu._is_active_element([OL(), 1, 2, 3]) is True


class TestIsSpecialNode:

    def test_is_not_special(self):
        assert mu._is_special_node(None) is False
        assert mu._is_special_node("foo") is False
        assert mu._is_special_node([]) is False
        assert mu._is_special_node(["foo"]) is False

    def test_is_special(self):
        assert mu._is_special_node(["$comment"]) is True
        assert mu._is_special_node(["$cdata"]) is True
        assert mu._is_special_node(["$pi"]) is True
        assert mu._is_special_node(["$foo"]) is True
        assert mu._is_special_node(["$raw"]) is True


class TestHasAttributes:

    # FIXME URL values should be handled differently
    def test_has_not(self):
        assert mu.has_attrs(None) is False
        assert mu.has_attrs("foo") is False
        assert mu.has_attrs([]) is False
        assert mu.has_attrs(["foo"]) is False
        assert mu.has_attrs(["foo", {}]) is False
        assert mu.has_attrs(["foo", "bla", {"a": 10}]) is False

    def test_has(self):
        assert mu.has_attrs(["foo", {"a": 10, "b": 20}]) is True
        assert mu.has_attrs(["foo", {"a": 10, "b": 20}, "bla"]) is True


class TestIsEmpty:

    def test_is_empty(self):
        assert mu.is_empty("foo") is False
        assert mu.is_empty(["foo"]) is True
        assert mu.is_empty(["foo", {}]) is True
        assert mu.is_empty(["foo", (1, 2, 3)]) is False


class TestAttributeFormatting:

    def test_escaping(self):
        # escape double quotes (required with foo="bar")
        assert mu._format_attrs({"foo": '"hi"'}) == ' foo="&quot;hi&quot;"'
        # note that one would expect this to be output as &apos;
        # but not a problem
        assert mu._format_attrs({"foo": "'hi'"}) == ' foo="&#x27;hi&#x27;"'
        # always escape &
        assert mu._format_attrs({"foo": "Q&A"}) == ' foo="Q&amp;A"'
        # always escape < and >
        assert mu._format_attrs({"foo": "<foo/>"}) == ' foo="&lt;foo/&gt;"'


class TestElementTextFormatting:

    def test_escaping(self):
        pass


class TestCreateNode:

    def test_empty_element(self):
        assert mu.markup(["foo"]) == "<foo/>"

    def test_element_with_attributes(self):
        assert mu.markup(["foo", {"a": 10, "b": 20}]) == '<foo a="10" b="20"/>'

    def test_element_without_attributes(self):
        assert mu.markup(["foo", {}]) == "<foo/>"

    def test_element_with_content(self):
        assert mu.markup(["foo", "bla"]) == "<foo>bla</foo>"

    def test_element_with_content_and_attributes(self):
        assert (
            mu.markup(["foo", {"a": 10, "b": 20}, "bla"])
            == '<foo a="10" b="20">bla</foo>'
        )

    def test_element_seq(self):
        assert mu.markup(["a"], ["b"], ["c"]) == "<a/><b/><c/>"


class TestDoc:

    def test_doc_with_empty_element(self):
        assert mu.markup(["foo", ["bar"]]) == "<foo><bar/></foo>"

    def test_doc_with_text_newlines(self):
        assert (
            mu.markup(["foo", ["bar", "foo", "\n", "bar", "\n"]])
            == "<foo><bar>foo\nbar\n</bar></foo>"
        )


class TestDocWithNamespaces:

    def test_doc_with_empty_element(self):
        assert (
            mu.markup(["x:foo", ["y:bar", {"m:a": 10, "b": 20}]])
            == '<x:foo><y:bar b="20" m:a="10"/></x:foo>'
        )


class TestDocWithSpecialNodes:

    def test_doc_with_comments(self):
        # FIXME no -- allowed
        assert mu.markup(["$comment", "bla&<>"]) == "<!-- bla&<> -->"

    def test_doc_with_cdata(self):
        # FIXME no ]]> allowed, could escape as ]]&gt;
        #       (in normal content already handled by always escaping >)
        assert mu.markup(["$cdata", "bla&<>"]) == "<![CDATA[bla&<>]]>"

    def test_doc_with_processing_instruction(self):
        # FIXME no ?> allowed
        assert (
            mu.markup(["$pi", 'xml version="1.0" encoding="UTF-8"'])
            == '<?xml version="1.0" encoding="UTF-8"?>'
        )

    def test_doc_with_invalid_special_node(self):
        assert mu.markup(["$foo", "bla"]) == ""


class TestTagFormatting:
    # FIXME html, xhtml have particular rules re self-closing or not
    #       these elements are:
    #       area, base, br, col, command, embed, hr, img, input, keygen,
    #       link, meta, param, source, track, wbr
    def test_empty_elements(self):
        assert mu.markup(["img"]) == "<img/>"
        assert mu.markup(["img", {"src": "foo"}]) == '<img src="foo"/>'
        assert mu.markup(["img"], mode=mu.Mode.XHTML) == "<img />"
        assert mu.markup(["img"], mode=mu.Mode.HTML) == "<img>"
        assert mu.markup(["img"], mode=mu.Mode.SGML) == "<img>"


class TestGetAttr:

    def test_get_attr(self):
        assert mu.get_attr("a", ["x", {"a": 10}]) == 10
        assert mu.get_attr("a", ["x", {"b": 10}], 20) == 20
        with pytest.raises(ValueError):
            mu.get_attr("a", "x", 20)


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
