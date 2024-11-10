from __future__ import annotations

from mu import apply
from mu import expand
from mu import markup
from mu import Node


class UL(Node):

    def mu(self):
        ul = ["ul"]
        if len(self._attrs) > 0:
            ul.append(self._attrs)
        for item in self._content:
            ul.append(["li", item])
        return ul


class TestMuContentWithNulls:

    def test_nulls_in_content(self):
        assert markup(["xml", {}]) == "<xml/>"
        assert markup(["xml", None, None]) == "<xml/>"
        assert markup(["xml", None, 1, None, 2]) == "<xml>12</xml>"


class TestMuContentList:

    def test_simple_seq_with_list_content(self):
        assert markup(["foo", (1, 2, 3)]) == "<foo>123</foo>"
        assert markup(["foo", "a", "b"]) == "<foo>ab</foo>"
        assert markup(["foo", ("a", "b")]) == "<foo>ab</foo>"
        assert markup(["foo", ("a", ("b"))]) == "<foo>ab</foo>"
        assert markup(["foo", [(1), "b"]]) == "<foo>1b</foo>"
        assert markup(["foo", [("a"), ("b"), "c"]]) == "<foo><a>bc</a></foo>"


class TestMuObjects:

    def testMuObject(self):
        assert (
            markup(["foo", UL(1, 2, 3)])
            == "<foo><ul><li>1</li><li>2</li><li>3</li></ul></foo>"
        )

    def testMuObjectElement(self):
        assert (
            markup(["foo", [UL(), 1, 2, 3]])
            == "<foo><ul><li>1</li><li>2</li><li>3</li></ul></foo>"
        )
        assert markup(["foo", [UL(), (1, 2, 3)]]) == "<foo><ul><li>123</li></ul></foo>"
        assert (
            markup(["foo", [UL(), {}, (1, 2, 3)]]) == "<foo><ul><li>123</li></ul></foo>"
        )
        assert (
            markup(["foo", [UL(), {"class": ("foo", "bar")}, 1, 2]])
            == '<foo><ul class="foo bar"><li>1</li><li>2</li></ul></foo>'
        )


class TestApply:

    def test_apply(self):

        assert apply(
            ["doc", ["foo", {"class": "x"}, "item 1", "item 2"]], {"foo": UL()}
        ) == ["doc", ["ul", {"class": "x"}, ["li", "item 1"], ["li", "item 2"]]]

        assert apply(["doc", ["$foo"], ["bar"], ["$foo"]], {"$foo": ["BAR"]}) == [
            "doc",
            ["BAR"],
            ["bar"],
            ["BAR"],
        ]


class TestExpand:

    def test_expand(self):

        assert expand(
            ["div", [UL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]]
        ) == [
            "div",
            [
                "ul",
                {"class": ("foo", "bar")},
                ["li", "item 1"],
                ["li", "item 2"],
                ["li", "item 3"],
            ],
        ]


class TestNode:

    def test_node_ctr(self):
        assert expand(
            [UL("item 1", "item 2", "item 3", id=123, cls=("foo", "bar"))]
        ) == [
            "ul",
            {"id": 123, "class": ("foo", "bar")},
            ["li", "item 1"],
            ["li", "item 2"],
            ["li", "item 3"],
        ]
