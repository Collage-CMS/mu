from __future__ import annotations

from mu import apply
from mu import Node


class UL(Node):
    def __init__(self, **attrs):
        super().__init__("ul", **attrs)

    def __call__(self, *nodes, **attrs):
        nodes = [["li", node] for node in nodes]
        return super().__call__(*nodes, **attrs)


class TestApply:
    def test_no_rules(self):
        assert apply(["foo"], {}) == ["foo"]
        assert apply(["foo", ["bar", {"a": 1, "b": 2}, "bla bla"]], {}) == [
            "foo",
            ["bar", {"a": 1, "b": 2}, "bla bla"],
        ]

    def test_replace_rule(self):
        assert apply(["foo"], {"foo": ["bar", {"class": "x"}, "bla", "bla"]}) == [
            "bar",
            {"class": "x"},
            "bla",
            "bla",
        ]

    def test_replace_obj(self):
        assert apply(["foo"], {"foo": UL()}) == ["ul"]
        assert apply(["foo", {"class": "x"}, "item 1", "item 2"], {"foo": UL()}) == [
            "ul",
            {"class": "x"},
            ["li", "item 1"],
            ["li", "item 2"],
        ]
