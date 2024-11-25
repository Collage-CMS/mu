from __future__ import annotations

import mu


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
        return mu._markup(self.mu())


class TestExpand:

    def test_expand_mu(self):
        # mu without any extra stuff should just reproduce the
        # same structure with None removed.
        assert mu.expand([]) == []
        assert mu.expand([1, 2, 3]) == [1, 2, 3]
        assert mu.expand([1, None, 2, None, 3]) == [1, 2, 3]
        assert mu.expand([(1), 2, (3)]) == [1, 2, 3]
        assert mu.expand(["foo", {}, "bar"]) == ["foo", "bar"]

    def test_expand_mu_with_objects(self):
        assert mu.expand([OL()]) == ["ol"]
        assert mu.expand(OL()) == ["ol"]
        assert mu.expand([OL(), 1, 2, 3]) == ["ol", ["li", 1], ["li", 2], ["li", 3]]
        assert mu.expand([OL(), {"class": ("foo", "bar")}, 1, 2, 3]) == [
            "ol",
            {"class": ("foo", "bar")},
            ["li", 1],
            ["li", 2],
            ["li", 3],
        ]
