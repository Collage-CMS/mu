from __future__ import annotations

import pytest

import mu
from mu import html
from mu import xml

# from mu import sgml
# from mu import xhtml


# TODO Add functions to manipulate Mu structures.
# TODO Add namespaces and generate well-formed XML (or auto-gen at top)


class OL(mu.Node):
    def __init__(self, *items):
        self.content = list(items)
        self.attrs = {}

    def mu(self):
        ol = ["ol"]
        if len(self.attrs) > 0:
            ol.append(self.attrs)
        for item in self.content:
            ol.append(["li", item])
        return ol

    def xml(self):
        return mu._markup(self.mu())


class TestTagNames:
    def test_basic_tags(self):
        assert xml(["div"]) == "<div/>"

    def test_tag_syntax_sugar(self):
        assert html(["div#foo"]) == '<div id="foo"/>'
        assert html(["div.foo"]) == '<div class="foo"/>'
        assert html(["div.foo", "bar", "baz"]) == '<div class="foo">barbaz</div>'
        assert html(["div.a.b"]) == '<div class="a b"/>'
        assert html(["div#foo.bar.baz"]) == '<div class="bar baz" id="foo"/>'


class TestAccessors:
    def test_tag(self):
        assert mu.tag(["foo"]) == "foo"
        assert mu.tag(["$foo"]) == "$foo"

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


class TestNotElement:
    def test_tag(self):
        with pytest.raises(ValueError):
            assert mu.tag(None) is None
        with pytest.raises(ValueError):
            assert mu.tag(0) is None
        with pytest.raises(ValueError):
            assert mu.tag([]) is None
        with pytest.raises(ValueError):
            assert mu.tag({}) is None


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


class TestGetAttr:
    def test_get_attr(self):
        assert mu.get_attr("a", ["x", {"a": 10}]) == 10
        assert mu.get_attr("a", ["x", {"b": 10}], 20) == 20
        with pytest.raises(ValueError):
            mu.get_attr("a", "x", 20)
