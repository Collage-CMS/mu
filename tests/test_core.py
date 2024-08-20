from __future__ import annotations

import mu as mu
import mu.json as jsn
import mu.yaml as yml

# TODO Needs much more checking on valid QNames, illegal constructs etc.
# TODO Add functions to manipulate Mu structures.
# TODO Add namespaces and generate well-formed XML (or auto-gen at top)


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


class TestHasAttributes:

    # FIXME URL values should be handled differently
    def test_has_not(self):
        assert mu._has_attrs(None) is False
        assert mu._has_attrs("foo") is False
        assert mu._has_attrs([]) is False
        assert mu._has_attrs(["foo"]) is False
        assert mu._has_attrs(["foo", {}]) is False
        assert mu._has_attrs(["foo", "bla", {"a": 10}]) is False

    def test_has(self):
        assert mu._has_attrs(["foo", {"a": 10, "b": 20}]) is True
        assert mu._has_attrs(["foo", {"a": 10, "b": 20}, "bla"]) is True


class TestIsEmpty:

    def test_is_empty(self):
        assert mu._is_empty("foo") is False
        assert mu._is_empty(["foo"]) is True
        assert mu._is_empty(["foo", {}]) is True
        assert mu._is_empty(["foo", (1, 2, 3)]) is False


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


class TestJsonMu:

    def test_json_mu(self):
        json = """
["foo", "bar"]
"""
        assert jsn.mu(json) == ["foo", "bar"]

        json = """
["foo", ["bar"]]
"""
        assert jsn.mu(json) == ["foo", ["bar"]]

    def test_mu_json(self):

        assert jsn.read(["foo"]) == '["foo"]'
        assert jsn.read(["foo", {"x": 10}, "bla"]) == '["foo", {"x": 10}, "bla"]'


class TestYamlMu:

    def test_yaml_mu(self):
        yaml = """
- foo
- bar
"""
        assert yml.mu(yaml) == ["foo", "bar"]

        yaml = """
- foo
- - bar
"""
        assert yml.mu(yaml) == ["foo", ["bar"]]

        yaml = """
- foo
- - bar
  - foo: 10
    bar: 20
  - blabla
"""
        assert yml.mu(yaml) == ["foo", ["bar", {"foo": 10, "bar": 20}, "blabla"]]

    def test_mu_yaml(self):

        assert yml.read(["foo"]) == "- foo\n"
        assert yml.read(["foo", {"x": 10}, "bla"]) == "- foo\n- x: 10\n- bla\n"


class TestTagFormatting:
    # FIXME html, xhtml have particular rules re self-closing or not
    #       these elements are:
    #       area, base, br, col, command, embed, hr, img, input, keygen,
    #       link, meta, param, source, track, wbr
    def test_empty_elements(self):
        assert mu.markup(["img"]) == "<img/>"
        assert mu.markup(["img", {"src": "foo"}]) == '<img src="foo"/>'
        assert mu.markup(["img"], mode="xhtml") == "<img />"
        assert mu.markup(["img"], mode="html") == "<img>"
        assert mu.markup(["img"], mode="sgml") == "<img>"
