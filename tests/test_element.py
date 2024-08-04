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


class TestUnorderedList:

    def test_unordered_list(self):
        assert el.unordered_list("foo", "bar", "baz") == [
            "ul",
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
