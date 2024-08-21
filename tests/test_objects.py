from __future__ import annotations

import mu
from mu import Node


class UL(Node):

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


class TestMuContentWithNulls:

    def test_nulls_in_content(self):
        assert mu.markup(["xml", {}]) == "<xml/>"
        assert mu.markup(["xml", None, None]) == "<xml/>"
        assert mu.markup(["xml", None, 1, None, 2]) == "<xml>12</xml>"


class TestMuContentList:

    def test_simple_seq_with_list_content(self):
        assert mu.markup(["foo", (1, 2, 3)]) == "<foo>123</foo>"
        assert mu.markup(["foo", "a", "b"]) == "<foo>ab</foo>"
        assert mu.markup(["foo", ("a", "b")]) == "<foo>ab</foo>"
        assert mu.markup(["foo", ("a", ("b"))]) == "<foo>ab</foo>"
        assert mu.markup(["foo", [(1), "b"]]) == "<foo>1b</foo>"
        assert mu.markup(["foo", [("a"), ("b"), "c"]]) == "<foo><a>bc</a></foo>"


class TestMuObjects:

    def testMuObject(self):
        assert (
            mu.markup(["foo", UL(1, 2, 3)])
            == "<foo><ol><li>1</li><li>2</li><li>3</li></ol></foo>"
        )

    def testMuObjectElement(self):
        assert (
            mu.markup(["foo", [UL(), 1, 2, 3]])
            == "<foo><ol><li>1</li><li>2</li><li>3</li></ol></foo>"
        )
        assert (
            mu.markup(["foo", [UL(), (1, 2, 3)]]) == "<foo><ol><li>123</li></ol></foo>"
        )
        assert (
            mu.markup(["foo", [UL(), {}, (1, 2, 3)]])
            == "<foo><ol><li>123</li></ol></foo>"
        )
        assert (
            mu.markup(["foo", [UL(), {"class": ("foo", "bar")}, 1, 2]])
            == '<foo><ol class="foo bar"><li>1</li><li>2</li></ol></foo>'
        )
