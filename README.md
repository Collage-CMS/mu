# Mu for Python

Represent HTML and XML using Python data structures. Based on the Clojure
library Hiccup created by James Reeves.

Also has interop functions for the [SaxonC-HE API](https://www.saxonica.com/saxon-c/index.xml)
via [`saxonche`](https://pypi.org/project/saxonche).

## Install

```
pip install py-mu
```

## Usage

TBD

## Documentation

### Special Nodes

Every `tag` that starts with `$` is a special node. For XML, however, only
`$comment`, `$pi`, and `$cdata` are meaningful.

### Wrappers


## Related work

- [weavejester/hiccup](https://github.com/weavejester/hiccup)
- [nbessi/pyhiccup](https://github.com/nbessi/pyhiccup)
- [Arkelis/hyccup](https://github.com/Arkelis/hyccup)
