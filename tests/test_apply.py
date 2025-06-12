from __future__ import annotations

import mu


class UL(mu.Node):
    def __init__(self, *items):
        self.content = list(items)
        self.attrs = {}

    def mu(self):
        ol = ["ul"]
        if len(self.attrs) > 0:
            ol.append(self.attrs)
        for item in self.content:
            ol.append(["li", item])
        return ol

    def xml(self):
        return mu.xml(self.mu())


class TestApply:
    def test_no_rules(self):
        assert mu.apply(["foo"], {}) == ["foo"]
        assert mu.apply(["foo", ["bar", {"a": 1, "b": 2}, "bla bla"]], {}) == [
            "foo",
            ["bar", {"a": 1, "b": 2}, "bla bla"],
        ]

    def test_replace_rule(self):
        assert mu.apply(["foo"], {"foo": ["bar", {"class": "x"}, "bla", "bla"]}) == [
            "bar",
            {"class": "x"},
            "bla",
            "bla",
        ]

    def test_replace_obj(self):
        assert mu.apply(["foo"], {"foo": UL()}) == ["ul"]
        assert mu.apply(["foo", {"class": "x"}, "item 1", "item 2"], {"foo": UL()}) == [
            "ul",
            {"class": "x"},
            ["li", "item 1"],
            ["li", "item 2"],
        ]
