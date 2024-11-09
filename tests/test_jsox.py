from __future__ import annotations

from mu.jsox import dump
from mu.jsox import load


class Foo:
    pass


class Bar:

    def mu(self):
        return ["$yo!"]


class Baz:

    def mu(self):
        return ["x", "bla"]


def foobar():
    pass


class TestLoad:

    def test_jsox_load_atomic(self):
        assert load(1) == 1
        assert load(0.2) == 0.2
        assert load("a") == "a"
        assert load([]) == []
        assert load(False) is False
        assert load(None) is None

    def test_jsox_load_element(self):
        assert load(["a"]) is None
        assert load(["a", 10]) == 10
        assert load(["a", 1, 2, 3]) == [1, 2, 3]

    def test_jsox_load_object(self):

        assert load(["_", {"as": "object"}]) == {}

        assert load(["_", {"as": "object"}, 10, 20, 30]) == {1: 10, 2: 20, 3: 30}

        assert load(["_", {"as": "object"}, ["a", 10], ["b", 20], ["c", 30]]) == {
            "a": 10,
            "b": 20,
            "c": 30,
        }

        assert load(
            [
                "_",
                {"as": "object"},
                ["a", 10, 11, 12],
                ["b", 20, 21, 22],
                ["c", 30, 31, 32],
            ]
        ) == {"a": [10, 11, 12], "b": [20, 21, 22], "c": [30, 31, 32]}

        assert load(["_", {"as": "object"}, "x", "y", "z"]) == {1: "x", 2: "y", 3: "z"}

        assert load(
            ["_", {"as": "object"}, ["a", "x", "y", "z"], ["b", "e", "f", "g"]]
        ) == {"a": ["x", "y", "z"], "b": ["e", "f", "g"]}

    def test_jsox_load_array(self):

        assert load(["_", {"as": "array"}]) == []

        assert load(["_", {"as": "array"}, 10, 20, 30]) == [10, 20, 30]

        assert load(["_", {"as": "array"}, ["_", 10], ["_", 20], ["_", 30]]) == [
            10,
            20,
            30,
        ]

        assert load(
            [
                "_",
                {"as": "array"},
                ["_", 10, 11, 12],
                ["_", 20, 21, 22],
                ["_", 30, 31, 32],
            ]
        ) == [[10, 11, 12], [20, 21, 22], [30, 31, 32]]

    def test_jsox_load_bool(self):

        assert load(["_", {"as": "boolean", "value": "true()"}]) is True
        assert load(["_", {"as": "boolean", "value": "false()"}]) is False

    def test_jsox_load_none(self):

        assert load(["_", {"as": "null"}]) is None

        # ??? raise ValueError when there is a value? or just ignore
        assert load(["_", {"as": "null"}, 1, 2, 3]) is None


class TestDump:

    def test_jsox_dump_atomic(self):

        assert dump(10) == ["_", {"as": "integer"}, 10]
        assert dump(10) == ["_", {"as": "integer"}, 10]

    def test_jsox_dump_object(self):

        assert dump({"x": 10}) == ["_", {"as": "object"}, ["x", {"as": "integer"}, 10]]

        assert dump({"x": 10, "y": "abc"}) == [
            "_",
            {"as": "object"},
            ["x", {"as": "integer"}, 10],
            ["y", "abc"],
        ]

        assert dump({"x": 10, "y": True}) == [
            "_",
            {"as": "object"},
            ["x", {"as": "integer"}, 10],
            ["y", {"as": "boolean", "value": "true()"}],
        ]

    def test_jsox_dump_array(self):

        assert dump([1, 2, 3]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "integer"}, 2],
            ["_", {"as": "integer"}, 3],
        ]

        assert dump([1, "2", False]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", "2"],
            ["_", {"as": "boolean", "value": "false()"}],
        ]

    def test_jsox_dump_nested(self):

        assert dump([1, [2, 3, True], 4]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            [
                "_",
                {"as": "array"},
                ["_", {"as": "integer"}, 2],
                ["_", {"as": "integer"}, 3],
                ["_", {"as": "boolean", "value": "true()"}],
            ],
            ["_", {"as": "integer"}, 4],
        ]

        # not sure what to do with this. It's a valid data structure but already Mu form
        # what to do with attribute values?

        assert dump(
            ["x", ["y", ["z", {"id": ("a", "b", "c"), "class": "foo"}, 1, 2, 3]]]
        ) == [
            "_",
            {"as": "array"},
            ["_", "x"],
            [
                "_",
                {"as": "array"},
                ["_", "y"],
                [
                    "_",
                    {"as": "array"},
                    ["_", "z"],
                    [
                        "_",
                        {"as": "object"},
                        ["id", {"as": "array"}, ["_", "a"], ["_", "b"], ["_", "c"]],
                        ["class", "foo"],
                    ],
                    ["_", {"as": "integer"}, 1],
                    ["_", {"as": "integer"}, 2],
                    ["_", {"as": "integer"}, 3],
                ],
            ],
        ]

    def test_jsox_dump_classes(self):

        assert dump(Foo()) == ["_", {"as": "null"}]

        assert dump(Bar()) == ["_", {"as": "mu"}, ["$yo!"]]

        assert dump({"a": Foo(), "b": Bar()}) == [
            "_",
            {"as": "object"},
            ["a", {"as": "null"}],
            ["b", {"as": "mu"}, ["$yo!"]],
        ]

    def test_jsox_dump_xml_object(self):

        assert dump(Baz()) == ["_", {"as": "mu"}, ["x", "bla"]]

    def test_jsox_dump_functions(self):

        assert dump(foobar) == ["_", {"as": "null"}]

    def test_jsox_dump_none(self):

        assert dump([1, None]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "null"}],
        ]

    def test_jsox_dump_empty_array(self):

        assert dump([1, []]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "array"}],
        ]

    def test_jsox_dump_emtpy_dict(self):

        assert dump([1, {}]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "object"}],
        ]

    def test_jsox_dump_float(self):

        assert dump([1, 1.0]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "float"}, 1.0],
        ]

    def test_jsox_dump_complex(self):

        # not sure how to represent complex numbers in Mu

        assert dump([1, 1j]) == [
            "_",
            {"as": "array"},
            ["_", {"as": "integer"}, 1],
            ["_", {"as": "complex"}, 1j],
        ]
