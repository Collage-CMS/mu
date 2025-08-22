from __future__ import annotations

from ast import literal_eval

with open("foo.mu", "r") as file:
    data = file.read()

print(literal_eval(data))
