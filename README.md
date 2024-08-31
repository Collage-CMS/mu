# Mu

Represent HTML and XML using Python data structures. This does for Python what the [Hiccup](https://github.com/weavejester/hiccup) library by James Reeves did for the Clojure language.


## Install

```shell
pip install mu
```


## Usage

To render a Mu data structure as markup (XML, XHTML or HTML) use the `mu.markup` function.

```python
import mu

mu.markup(["p", "Hello, ", ["b", "World"], "!"])
```

Returns the string `<p>Hello, <b>World</b>!</p>`


## Documentation

In XML or related markup (XHTML, HTML, SGML) a data structure is made up of various node types such as element, attribute, or text nodes.

However, writing markup in code is tedious and error-prone. Mu allows creating well-formed markup with Python code and basic Python data structures.

### Element nodes

An element node is made up of a tag, an optional attribute dictionary and zero or more content nodes which themselves can be made up of other elements.

```python
el = ["p", {"id": 1}, "this is a paragraph."]
```

You can access the parts of this element node using accessor functions.

```python
mu.tag(el)       # "p"
mu.attrs(el)     # {"id": 1}
mu.content(el)   # ["this is a paragraph."]
```

To render this as XML markup:

```python
mu.markup(el)    # <p id="1">this is a paragraph.</p>
```

Use the provided predicate functions to inspect a node.

```python
mu.is_element(el)       # is this a valid element node?
mu.is_special_node(el)  # is this a special node? (see below)
mu.is_empty(el)         # does it have child nodes?
mu.has_attrs(el)        # does it have attributes?
```

### Render markup

The `mu.markup` function may have a keyword argument that specifies the type of markup generated. Although XML, XHTML, HTML look very similar there are some slight differences mainly to how empty elements are rendered.

```python
mu.markup(["img"], mode="xml")     # <img/>
mu.markup(["img"], mode="xhtml")   # <img />
mu.markup(["img"], mode="html")    # <img>
mu.markup(["script"], mode="html") # <script></script>
```

Note that Mu tries to do the correct thing when the markup mode is HTML.

### Special nodes

XML has a few syntactic constructs that you usually don't need. But if you do need them, you can represent them in Mu as follows.

```python
["$comment", "this is a comment"]
["$pi", "foo", "bar"]
["$cdata", "<foo>"]
["$raw", "<foo/>"]
```

These will be rendered as:

```xml
<!-- this is a comment -->
<?foo bar?>
&lt;foo&gt;
<foo/>
```

Every tag name that starts with `$` is considered a special node. Special nodes other than the ones mentioned above will simply disappear from the markup returned by `markup`. Note that they will remain in the nodes returned from `expand`.

A `$cdata` node will not escape it's content as is usual in XML and HTML. A `$raw` node is very useful for adding string content that already contains markup.


### Namespaces

Mu does not enforce XML rules. You can use namespaces but you have to provide the namespace declarations as is expected by [XML Namespaces](https://www.w3.org/TR/xml-names).

```python
["svg", {"xmlns": "http://www.w3.org/2000/svg"},
  ["rect", {"width": 200, "height": 100, "x": 10, "y": 10}]
]
```

```xml
<svg xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="100" x="10" y="10"/>
</svg>
```

The following uses explicit namespace prefixes and is semantically identical to the previous example.

```python
["svg:svg", {"xmlns:svg": "http://www.w3.org/2000/svg"},
  ["svg:rect", {"width": 200, "height": 100, "x": 10, "y": 10}]
]
```

```xml
<svg:svg xmlns:svg="http://www.w3.org/2000/svg">
  <svg:rect widht="200" height="100" x="10" y="10"/>
</svg:svg>
```

### Object nodes

Object nodes may appear in two positions inside a Mu data structure.

1) In the content position of an element node (e.g. `["p", {"class": "x"}, obj]`) or,
2) In the tag position of an element node (e.g. `[obj, {"class": "x"}, "content"]`)

In both cases the object's `xml` method is called when rendered into markup. The `xml` method is always called without any arguments. However, when the object appears in the tag position then the attributes dict is passed to the object using its `set_attr` method, and the content nodes are passed using the `set_content` method.

Object nodes have to be derived from the `mu.Node` class and must implement two methods: `mu` and `xml`. The `markup` function will call the object's `xml` method. The `expand` function will call the object's `mu` method.

As an example take the following custom class definition.

```python
class OL(mu.Node):

    def mu(self):
        ol = ["ol"]
        if len(self._attrs) > 0:
            ol.append(self._attrs)
        for item in self._content:
            ol.append(["li", item])
        return ol

    def xml(self):
        return mu.markup(self.mu())
```

- This class is defined as a subclass from the `mu.Node` class.
- The `mu` method builds an order list element and list item for each content item.
- The `xml` method calls the `mu` method and renders it as XML markup.

Now let's use this class in a Mu data structure.

```python
mu.markup(["div", OL(), "foo"])
```

```xml
<div><ol/>foo</div>
```

Here the `OL()` object is in the content position so no information is passed to it to render a list. This may not be what you wanted to achieve.

To produce a list the object must be in the tag position of an element node.

```python
mu.markup(["div", [OL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
```

```xml
<div>
  <ol class="foo bar">
    <li>item 1</li>
    <li>item 2</li>
    <li>item 3</li>
  </ol>
</div>
```

### Expand nodes

In some cases you may want to use the `mu.expand` function to only expand object nodes to a straightforward data structure.

```python
mu.expand(["div", [OL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
```

```python
["div",
  ["ol", {"class": ("foo", "bar")},
    ["li", "item 1"],
    ["li", "item 2"],
    ["li", "item 3"]]]
```

### Apply nodes

A third and final method of building a document is `mu.apply`. It gets a dictionary with rules. The values of the dictionar are either a replacement value or a `mu.Node` (or something that looks like one).

Using the previous example of the `UL` object we can illustrate how `my.apply` works.

Say we have a Mu data structure in which we want to replace each `foo` element with an unordered list node object.

```python
mu.apply(
  ["doc", ["foo", {"class" "x"}, "item 1", "item 2"]],
  {"foo": OL()})
```

```python
["doc",
  ["ol", {"class": "x"}, ["li", "item 1"], ["li", "item 2"]]]
```

You can also pass in literal values that get replaced when the element name matches a rule.

```python
mu.apply(
  ["doc", ["$foo"], ["bar"], ["$foo"]],
  {"$foo": ["BAR"]})
```

```python
["doc",
  ["BAR"],["bar"], ["BAR"]]
```

Note that when object nodes are found they won't get expanded unless they are present in the rules dictionary.


## Related work

- [SXML](https://en.wikipedia.org/wiki/SXML)
- [weavejester/hiccup](https://github.com/weavejester/hiccup)
- [nbessi/pyhiccup](https://github.com/nbessi/pyhiccup)
