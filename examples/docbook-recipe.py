from __future__ import annotations

import importlib

import mu
from mu import expand
from mu import Node
from mu import xml

importlib.reload(mu)


class sect1(Node):

    def mu(self):
        sect1 = ["sect1"]
        len(self._attrs) > 0 and sect1.append(self._attrs)
        sect1.extend(self._content)
        return sect1


class sect2(Node):

    def mu(self):
        sect2 = ["sect2"]
        len(self._attrs) > 0 and sect2.append(self._attrs)
        sect2.extend(self._content)
        return sect2


class ol(Node):

    def mu(self):
        ol = ["itemizedlist"]
        len(self._attrs) > 0 and ol.append(self._attrs)
        ol.extend([["listitem", node] for node in self._content])
        return ol


class p(Node):

    def mu(self):
        p = ["para"]
        len(self._attrs) > 0 and p.append(self._attrs)
        p.extend(self._content)
        return p


class title(Node):

    def mu(self):
        title = ["title"]
        len(self._attrs) > 0 and title.append(self._attrs)
        title.extend(self._content)
        return title


ingredients = [sect2([title("Ingredients"), p()])]
equipment = [sect2(title("Equipment"), p())]
what = [sect1([title("What do you need?"), ingredients, equipment])]
prep = [
    sect1(
        [
            title("Preparation"),
            ol(
                p("60g Habanero Chilis"),
                p("30g Cayenne Chilis"),
                p("1,5 Butch T Chilis"),
                p("75g Kidney Beans"),
            ),
        ],
        id="sec.preparation",
    )
]
recipe = [what, prep]

# expand should expand child objects too!
expand(recipe)

print(xml(recipe))