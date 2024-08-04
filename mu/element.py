from __future__ import annotations


def javascript_tag(script):
    """Wrap the javascript code in a script element and protect with CDATA section."""
    return ["script", {"type": "text/javascript"}, f"//<![CDATA[\n{script}\n//]]>"]


# TODO escape URI
def link_to(url, *content):
    """Creat a hyperlink element. If no content is given use url."""
    a = ["a", {"href": url}]
    a.extend(content) if content else a.append(url)
    return a


# TODO escape URI
def mail_to(email, *content):
    """Wrap email adress in a hyperlink element. If no content is given use email."""
    a = ["a", {"href": f"mailto:{email}"}]
    a.extend(content) if content else a.append(email)
    return a


def unordered_list(*items):
    """Wrap items in an unordered list element."""
    ul = ["ul"]
    ul.extend([["li", item] for item in items])
    return ul


def ordered_list(*items):
    """Wrap items in an ordered list element."""
    ol = ["ol"]
    ol.extend([["li", item] for item in items])
    return ol


# TODO escape URI
def images(src, alt=None):
    """Create an image element."""
    if alt:
        return ["img", {"src": src, "alt": alt}]
    else:
        return ["img", {"src": src}]
