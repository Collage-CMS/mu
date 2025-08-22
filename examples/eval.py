from __future__ import annotations

import mu

with open("examples/foo.mu", "r") as file:
    data = file.read()

at = compile(data, "examples/foo.mu", "eval")
# print(eval(at, {"__builtins__": {}}, {}))
print(mu.html(eval(at, {}, {})))
