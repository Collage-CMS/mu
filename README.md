# Mu

Represent HTML and XML using Python data structures. Based on the Clojure
library Hiccup created by James Reeves.

Used by [Collage](https://github.com/Collage-CMS/collage) CMS.


## Install

```
pip install mu
```

## Usage

```
import mu

mu.markup(["p", "Hello, ", ["b", "World"], "!"])
```

Returns the string `<p>Hello, <b>World</b>!`

## Documentation

### Special Nodes

Every `tag` that starts with `$` is a special node. But special nodes other
than `$comment`, `$pi`, and `$cdata` will be ignored.

### Elements

### Pages



## Related work

- [weavejester/hiccup](https://github.com/weavejester/hiccup)
- [nbessi/pyhiccup](https://github.com/nbessi/pyhiccup)
