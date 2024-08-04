from __future__ import annotations

import yaml


def mu(yml):
    """Convert YAML to Mu data structure."""
    return yaml.safe_load(yml)


def read(mu):
    """Convert Mu data structure to YAML."""
    return yaml.dump(mu)
