"""Print the authoring status of the first structured evidence pilot."""
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.services.pathway_evidence import audit, load_pilot


if __name__ == "__main__":
    result = audit(load_pilot())
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))
