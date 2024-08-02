from __future__ import annotations

import json


def mu(jsn):
    """Convert JSON to Mu data structure."""
    return json.loads(jsn)


def read(mu):
    """Convert Mu data structure to JSON."""
    return json.dumps(mu)
