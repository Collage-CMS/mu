# Tests that are copied from Hiccup tests
# https://github.com/weavejester/hiccup/tree/master/test
# to ensure that Mu is compatible or that we know where it deviates
from __future__ import annotations

import mu.element as el

# https://github.com/weavejester/hiccup/blob/master/test/hiccup/element_test.clj


class TestJavascriptTag:

    def test_javascript_tag(self):
        assert el.javascript_tag("alert('hello');") == [
            "script",
            {"type": "text/javascript"},
            "//<![CDATA[\nalert('hello');\n//]]>",
        ]


class TestLinkTo:

    def test_link_to(self):
        assert el.link_to("/") == ["a", {"href": "/"}, "/"]
        assert el.link_to("/", "foo") == ["a", {"href": "/"}, "foo"]
        assert el.link_to("/", "foo", "bar") == ["a", {"href": "/"}, "foo", "bar"]

    def test_link_to_with_attrs(self):
        assert el.link_to("/", attrs={"x": 10}) == ["a", {"href": "/", "x": 10}, "/"]
        assert el.link_to("/", "foo", attrs={"x": 10}) == [
            "a",
            {"href": "/", "x": 10},
            "foo",
        ]
        assert el.link_to("/", "foo", "bar", attrs={"x": 10}) == [
            "a",
            {"href": "/", "x": 10},
            "foo",
            "bar",
        ]


class TestMailTo:

    def test_mail_to(self):
        assert el.mail_to("foo@example.com") == [
            "a",
            {"href": "mailto:foo@example.com"},
            "foo@example.com",
        ]
        assert el.mail_to("foo@example.com", "foo") == [
            "a",
            {"href": "mailto:foo@example.com"},
            "foo",
        ]

    def test_mail_with_attrs(self):
        assert el.mail_to("foo@example.com", attrs={"x": 10}) == [
            "a",
            {"href": "mailto:foo@example.com", "x": 10},
            "foo@example.com",
        ]
        assert el.mail_to("foo@example.com", "foo", attrs={"x": 10}) == [
            "a",
            {"href": "mailto:foo@example.com", "x": 10},
            "foo",
        ]


class TestUnorderedList:

    def test_unordered_list(self):
        assert el.unordered_list("foo", "bar", "baz") == [
            "ul",
            ["li", "foo"],
            ["li", "bar"],
            ["li", "baz"],
        ]

    def test_unordered_list_with_attrs(self):
        assert el.unordered_list("foo", "bar", "baz", attrs={"x": 10}) == [
            "ul",
            {"x": 10},
            ["li", "foo"],
            ["li", "bar"],
            ["li", "baz"],
        ]


class TestOrderedList:

    def test_ordered_list(self):
        assert el.ordered_list("foo", "bar", "baz") == [
            "ol",
            ["li", "foo"],
            ["li", "bar"],
            ["li", "baz"],
        ]

    def test_ordered_list_with_attrs(self):
        assert el.ordered_list("foo", "bar", "baz", attrs={"x": 10}) == [
            "ol",
            {"x": 10},
            ["li", "foo"],
            ["li", "bar"],
            ["li", "baz"],
        ]


class TestWrapper:

    def test_wrap(self):
        wrapper = ["foo", {"x": 10}]
        result = ["foo", {"x": 10}, ["bar"], ["baz"]]
        assert el.wrap(wrapper, [["bar"], ["baz"]]) == result
