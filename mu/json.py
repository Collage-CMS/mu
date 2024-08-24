from __future__ import annotations

import json


def mu(data):
    """Convert JSON to Mu data structure."""
    return json.loads(data)


def read(data):
    """Convert Mu data structure to JSON."""
    return json.dumps(data)
