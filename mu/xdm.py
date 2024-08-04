from __future__ import annotations

from saxonche import PyXdmNode

# instead of proc.parse_x should we use PyDocumentBuilder?
# via proc.new_document_builder()


def mu(xdm: PyXdmNode):
    """Build a Mu data structure from an XDM node."""
    # NOTE in Saxon 13 axis navigation will be changed to use XdmNodeKind enum
    typ = xdm.node_kind_str
    if typ == "document":
        for node in xdm.children:
            return mu(node)
    elif typ == "element":
        el = []
        el.append(xdm.local_name)
        attrs = {}
        for attr in xdm.attributes:
            attrs[attr.local_name] = attr.string_value
        if len(attrs) > 0:
            el.append(attrs)
        for child in xdm.children:
            el.append(mu(child))
        return el
    # elif typ == 'attribute':
    #    pass
    elif typ == "text":
        return xdm.string_value
    elif typ == "comment":
        return "<!-- " + str(xdm) + " -->"
    elif typ == "processing-instruction":
        return "<?" + str(xdm) + "?>"
    elif typ == "namespace":
        return "#NS"
    else:  # typ == 'unknown'
        pass
