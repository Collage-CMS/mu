from __future__ import annotations

import mu as mu


class TestMuObjects:

    def test_simple_seq_with_list_content(self):
        assert mu.markup(["foo", (1, 2, 3)]) == "<foo>123</foo>"


if __name__ == "__repl__":

    import importlib

    importlib.reload(mu)
    mu.markup(["foo"], mode="html")

    mu.markup(["foo", (1, 2, 3)])

    mu.content(["foo", (1, 2, 3)])

    isinstance([], list)
    isinstance((), list)

    isinstance([], tuple)
    isinstance((), tuple)

    list((1, 2, 3))
    tuple([1, 2, 3])

    mu._is_empty("foo")
    mu._is_empty(["foo"])
    mu._is_empty(["foo", {}])
    mu._is_empty(["foo", (1, 2, 3)])

    mu.markup(["foo", {"a": 10}, "a", "b"])
    mu.markup(["foo", {"a": 10}, ("a", "b")])
    mu.markup(["foo", {"a": 10}, ("a", ("b"))])
    mu.markup(["foo", {"a": 10}, [(1), "b"]])
    mu.markup(["foo", {"a": 10}, [("a"), ("b"), "c"]])

    mu.markup(["xml", {}])  # "<xml/>"
    mu.markup(["xml", None, None])  # "<xml></xml>"
    mu.markup(["xml", None, 1, None, 2])  # "<xml></xml>"
