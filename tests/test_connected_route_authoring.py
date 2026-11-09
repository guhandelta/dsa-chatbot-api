import subprocess
from pathlib import Path


def test_connected_route_draft_examples_run_locally():
    root = Path(__file__).resolve().parents[1]
    result = subprocess.run(['node', str(root / 'tools/verify_connected_route.mjs')],
                            cwd=root, capture_output=True, text=True, timeout=10)
    assert result.returncode == 0, result.stderr
    assert 'boundaries passed' in result.stdout
