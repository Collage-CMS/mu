from __future__ import annotations

import py_mu as mu
import py_mu.json as jsn
import py_mu.yaml as yml


class TestAccessors:

    def test_tag(self):
        assert mu._tag(["foo"]) == "foo"
        assert mu._tag(["$foo"]) == "$foo"
        assert mu._tag(None) is None
        assert mu._tag(0) is None
        assert mu._tag([]) is None
        assert mu._tag({}) is None

    def test_no_attrs(self):
        assert mu._attrs(["foo"]) == {}
        assert mu._attrs(["foo", {}]) == {}
        assert mu._attrs(["foo", "bla", {"a": 10}]) == {}

    def test_attrs(self):
        assert mu._attrs(["foo", {"a": 10, "b": 20}]) == {"a": 10, "b": 20}


class TestIsElement:

    def test_is_not(self):
        assert mu._is_element([]) is False
        assert mu._is_element(0) is False
        assert mu._is_element(None) is False
        assert mu._is_element({}) is False
        assert mu._is_element("foo") is False
        assert mu._is_element(True) is False

    def test_is(self):
        assert mu._is_element(["foo"]) is True
        assert mu._is_element(["foo", ["bar"]]) is True
        assert mu._is_element(["foo", "bla"]) is True
        assert mu._is_element(["foo", {}, "bla"]) is True


class TestIsSpecialNode:

    def test_is_not(self):
        assert mu._is_special_node(["foo"]) is False
        assert mu._is_special_node(None) is False
        assert mu._is_special_node([]) is False

    def test_is(self):
        assert mu._is_special_node(["$comment"]) is True
        assert mu._is_special_node(["$cdata"]) is True
        assert mu._is_special_node(["$pi"]) is True
        assert mu._is_special_node(["$foo"]) is True


class TestHasAttributes:

    def test_has_not(self):
        assert mu._has_attrs(["foo"]) is False
        assert mu._has_attrs(["foo", {}]) is False
        assert mu._has_attrs(["foo", "bla", {"a": 10}]) is False

    def test_has(self):
        assert mu._has_attrs(["foo", {"a": 10, "b": 20}]) is True


class TestCreateNode:

    def test_empty_element(self):
        assert mu.xml(["foo"]) == "<foo/>"

    def test_element_with_attributes(self):
        assert mu.xml(["foo", {"a": 10, "b": 20}]) == '<foo a="10" b="20"/>'

    def test_element_without_attributes(self):
        assert mu.xml(["foo", {}]) == "<foo/>"

    def test_element_with_content(self):
        assert mu.xml(["foo", "bla"]) == "<foo>bla</foo>"

    def test_element_with_content_and_attributes(self):
        assert (
            mu.xml(["foo", {"a": 10, "b": 20}, "bla"]) == '<foo a="10" b="20">bla</foo>'
        )


class TestDoc:

    def test_doc_with_empty_element(self):
        assert mu.xml(["foo", ["bar"]]) == "<foo><bar/></foo>"

    def test_doc_with_text_newlines(self):
        assert (
            mu.xml(["foo", ["bar", "foo", "\n", "bar", "\n"]])
            == "<foo><bar>foo\nbar\n</bar></foo>"
        )


class TestDocWithNamespaces:

    def test_doc_with_empty_element(self):
        assert (
            mu.xml(["x:foo", ["y:bar", {"m:a": 10, "b": 20}]])
            == '<x:foo><y:bar m:a="10" b="20"/></x:foo>'
        )


class TestDocWithSpecialNodes:

    def test_doc_with_comments(self):
        XML = "<foo><!-- bla --></foo>"
        MU = ["foo", ["$comment", "bla"]]
        assert mu.xml(MU) == XML

    def test_doc_with_cdata(self):
        XML = "<foo><![CDATA[bla]]></foo>"
        MU = ["foo", ["$cdata", "bla"]]
        assert mu.xml(MU) == XML

    def test_doc_with_processing_instruction(self):
        XML = '<foo><?xml version="1.0" encoding="UTF-8"?></foo>'
        MU = ["foo", ["$pi", 'xml version="1.0" encoding="UTF-8"']]
        assert mu.xml(MU) == XML

    def test_doc_with_invalid_special_node(self):
        XML = "<foo></foo>"
        MU = ["foo", ["$foo", "bla"]]
        assert mu.xml(MU) == XML

    def test_doc_with_multiple(self):
        XML = "<foo><![CDATA[bla]]>bla<!-- !! --></foo>"
        MU = ["foo", ["$cdata", "bla"], "bla", ["$foo", "bar"], ["$comment", "!!"]]
        assert mu.xml(MU) == XML


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


# class TestXdmMu:
#
#    def test_mu_xdm(self):
#        assert type(xdm.read(["foo"])) == PyXdmNode
#
#    def test_mu_doc(self):
#        XML = "<foo>blabla<!-- !! --></foo>"
#        MU = ["foo", ["$cdata", "bla"], "bla", ["$foo", "bar"], ["$comment", "!!"]]
#        assert str(xdm.read(MU)) == XML


class TestWrapper:

    def test_wrap(self):
        wrapper = ["foo", {"x": 10}]
        result = ["foo", {"x": 10}, ["bar"], ["baz"]]
        assert mu.wrap(wrapper, ["bar"], ["baz"]) == result

    def test_xslt_wrapper(self):
        result = [
            "xsl:stylesheet",
            {"version": 3.0, "xmlns:xsl": "http://www.w3.org/1999/XSL/Transform"},
            ["xsl:template"],
        ]
        assert mu.xslt(["xsl:template"]) == result

    def test_svg_wrapper(self):
        result = ["svg", {"xmlns": "http://www.w3.org/2000/svg"}, ["rect"]]
        assert mu.svg(["rect"]) == result
