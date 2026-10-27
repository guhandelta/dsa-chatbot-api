"""Print the declared execution capabilities and actual local toolchain probes.

Run from dsa-chatbot-api: PYTHONPATH=. .venv/bin/python tools/audit_execution_capabilities.py
This is read-only. Docker probes require the configured image to be present.
"""
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.services.code_runner import available_languages
from app.services.execution_adapters import catalog


if __name__ == "__main__":
    print(json.dumps(catalog(available_languages()), indent=2, sort_keys=True))
