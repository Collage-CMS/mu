# Mu

<img src="docs/logo.png" width="200">

Represent XML using Python data structures. This does for Python what the [Hiccup](https://github.com/weavejester/hiccup) library by James Reeves did for the Clojure language.

Warning: this library is still alpha. So expect breaking changes.


## Usage

To render a Mu data structure as XML markup use the `xml` function.

```python
from mu import xml

xml(["p", "Hello, ", ["b", "World"], "!"])
```

Returns the string `<p>Hello, <b>World</b>!</p>`

Note that serializing to a string will not guarantee well-formed XML.


## Documentation

XML is a tree data structure made up of various node types such as element, attribute, or text nodes.

However, writing markup in code is tedious and error-prone. Mu allows creating markup with Python code and basic Python data structures.

### Element nodes

An element node is made up of a tag, an optional attribute dictionary and zero or more content nodes which themselves can be made up of other elements.

```python
el = ["p", {"id": 1}, "this is a paragraph."]
```

You can access the individual parts of an element node using the following accessor functions.

```python
import mu

mu.tag(el)            # "p"
mu.attrs(el)          # {"id": 1}
mu.content(el)        # ["this is a paragraph."]
mu.get_attr("id", el) # 1
```

To render this as XML markup:

```python
from mu import xml

xml(el)    # <p id="1">this is a paragraph.</p>
```

Use the provided predicate functions to inspect a node.

```python
import mu

mu.is_element(el)       # is this a valid element node?
mu.is_special_node(el)  # is this a special node? (see below)
mu.is_empty(el)         # does it have child nodes?
mu.has_attrs(el)        # does it have attributes?
```


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

Nodes with tag names that start with `$` are reserved for other applications. The `xml()` function will drop special nodes that it does not recognize.

A `$cdata` node will not escape it's content as is usual in XML and HTML. A `$raw` node is very useful for adding string content that already contains markup.

A `$comment` node will ensure that the forbidden `--` is not part of the comment text.


### Namespaces

Mu does not enforce XML rules. You can use namespaces but you have to provide the namespace declarations as is expected by [XML Namespaces](https://www.w3.org/TR/xml-names).

```python
["svg", dict(xmlns="http://www.w3.org/2000/svg"),
  ["rect", dict(width=200, height=100, x=10, y=10)]
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

Object nodes can be derived from the `mu.Node` class and must implement the `mu` method which should generate well-formed Mu data. This method will be called when rendering or expanding the Mu data structure.

As an example take the following custom class definition.

```python
import mu
from mu import xml

class OL(mu.Node):

    def mu(self):
        ol = ["ol"]
        if len(self._attrs) > 0:
            ol.append(self._attrs)
        for item in self._content:
            ol.append(["li", item])
        return ol
```

Let's use this class in a Mu data structure.

```python
xml(["div", OL(), "foo"])
```

```xml
<div><ol/>foo</div>
```

Here the `OL()` object is in the content position so no information is passed to it to render a list. This may not be what you wanted to achieve.

To produce a list the object must be in the tag position of an element node.

```python
xml(["div", [OL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
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

You can also provide some initial content and attributes in the object node constructor.

```python
xml(["div", [OL("item 1", id=1, cls=("foo", "bar")), "item 2", "item 3"]])
```

Note that we cannot use the reserved `class` keyword, instead use `cls` to get a `class` attribute. It is a bit of a hack.

```xml
<div>
  <ol class="foo bar" id="1">
    <li>item 1</li>
    <li>item 2</li>
    <li>item 3</li>
  </ol>
</div>
```

### Expand nodes

In some cases you may want to use the `mu.expand` function to only expand object nodes to a straightforward data structure.

```python
from mu import expand

expand(["div", [OL(), {"class": ("foo", "bar")}, "item 1", "item 2", "item 3"]])
```

```python
["div",
  ["ol", {"class": ("foo", "bar")},
    ["li", "item 1"],
    ["li", "item 2"],
    ["li", "item 3"]]]
```

### Apply nodes

A third and final method of building a document is `mu.apply`. It gets a dictionary with rules. The values of the dictionary are either a replacement value or a `mu.Node` (or something that looks like one).

Using the previous example of the `UL` object we can illustrate how `my.apply` works.

Say we have a Mu data structure in which we want to replace each `foo` element with an unordered list node object.

```python
from mu import apply

apply(
  ["doc", ["foo", {"class": "x"}, "item 1", "item 2"]],
  {"foo": OL()})
```

```python
["doc",
  ["ol", {"class": "x"}, ["li", "item 1"], ["li", "item 2"]]]
```

You can also pass in literal values that get replaced when the element name matches a rule.

```python
apply(
  ["doc", ["$foo"], ["bar"], ["$foo"]],
  {"$foo": ["BAR"]})
```

```python
["doc",
  ["BAR"],["bar"], ["BAR"]]
```

Note that when object nodes are found they won't get expanded unless they are present in the rules dictionary.

### Mu documents as YAML

Many Mu documents can be expressed as YAML quite elegantly.

```yml
[foo,[bar, {a: 1, class: bla}, just saying]]
```

Let's try something more complicated (a [Docbook cooking recipe](https://opensuse.github.io/daps/doc/art.tutorial.html)).

```yml
[
    [sect1,
        [title, What do you need?],
        [sect2,
            [title, Ingredients],
            [para]],
        [sect2,
            [title, Equipment],
            [para]]],
    [sect1, {id: sec.preparation},
        [title, Preparation],
        [itemizedlist,
            [listitem,
                [para, 60g Habanero Chilis]],
            [listitem,
                [para, 30g Cayenne Chilis]],
            [listitem,
                [para, "1,5 Butch T Chilis"]],
            [listitem,
                [para, 75g Kidney Beans]]]]
]
```

Etc. you get the idea. It's not ideal (e.g. some characters, such as commas, may require text to be quoted) and using coding we can make such documents using code.


### Mu documents as code

Whe can write code to help with certain structures. For example the list can be generated by an object node.

```python
# see examples/docbook-cooking.py
```


### Serializing Python data structures

```python
mu.dumps(["a",True,3.0])
```

```python
mu.loads(['_', {'as': 'array'},
  ['_', 'a'],
  ['_', {'as': 'boolean', 'value': 'true()'}],
  ['_', {'as': 'float'}, 3.0]])
```

```python
mu.dumps(dict(a="a",b=True,c=3.0))
```

```python
mu.loads(['_', {'as': 'object'},
  ['a', 'a'],
  ['b', {'as': 'boolean', 'value': 'true()'}],
  ['c', {'as': 'float'}, 3.0]])
```

When `dumps()` encounters a Python object it will call it's `mu()` method if it exists otherwise it will not be part of the serialized result. A function object will be called and it's return value becomes part of the serialized result.

## Develop

Install [uv](https://github.com/astral-sh/uv).

Run tests.

```shell
pytest tests/
```

Or with coverage.

```shell
pytest --cov-report term --cov=mu tests/
```


Run `mypy` type checking.

```shell
pip install mypy
mypy --config-file pyproject.toml ./
```


## Related work

- [SXML](https://en.wikipedia.org/wiki/SXML)
- [weavejester/hiccup](https://github.com/weavejester/hiccup)
- [nbessi/pyhiccup](https://github.com/nbessi/pyhiccup)
