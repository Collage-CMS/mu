from __future__ import annotations

import mu


class UL(object):

    def __init__(self, *items):
        self.items = items

    def mu(self):
        ol = ["ol"]
        for x in self.items:
            ol.append(["li", x])
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
