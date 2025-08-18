from __future__ import annotations

from mu import expand


class TestExpand:
    def test_expand_mu(self):
        # mu without any extra stuff should just reproduce the
        # same structure with None removed.
        assert expand([]) == []
        assert expand([1, 2, 3]) == [1, 2, 3]
        assert expand([1, None, 2, None, 3]) == [1, 2, 3]
        assert expand([(1), 2, (3)]) == [1, 2, 3]
        assert expand(["foo", {}, "bar"]) == ["foo", "bar"]


# TODO: more tests
