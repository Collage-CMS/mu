from __future__ import annotations


def javascript_tag(script, attrs: dict = {}):
    """Wrap the javascript code in a script element and protect with CDATA section."""
    return [
        "script",
        attrs | {"type": "text/javascript"},
        f"//<![CDATA[\n{script}\n//]]>",
    ]


# TODO escape URI
def link_to(url, *content, attrs: dict = {}):
    """Creat a hyperlink element. If no content is given use url."""
    a = ["a", attrs | {"href": url}]
    a.extend(content) if content else a.append(url)
    return a


# TODO escape URI
def mail_to(email, *content, attrs: dict = {}):
    """Wrap email adress in a hyperlink element. If no content is given use email."""
    a = ["a", attrs | {"href": f"mailto:{email}"}]
    a.extend(content) if content else a.append(email)
    return a


def unordered_list(*items, attrs: dict = {}):
    """Wrap items in an unordered list element."""
    el = ["ul"]
    if attrs:
        el.append(attrs)
    return wrap(el, [["li", item] for item in items])


def ordered_list(*items, attrs: dict = {}):
    """Wrap items in an ordered list element."""
    el = ["ol"]
    if attrs:
        el.append(attrs)
    return wrap(el, [["li", item] for item in items])


# TODO escape URI
def image(src, alt=None, attrs: dict = {}):
    """Create an image element."""
    if alt:
        return ["img", attrs | {"src": src, "alt": alt}]
    else:
        return ["img", attrs | {"src": src}]


def wrap(el: list | tuple, children=[]):
    """Wrap XML"""
    output = el
    output.extend(children)
    return output
