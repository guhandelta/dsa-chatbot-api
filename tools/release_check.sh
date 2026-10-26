#!/usr/bin/env bash
# Release check: the backend suite on the production execution backend.
#
# Go and C# checks skip when their toolchains are missing from the host, so
# the authoritative run uses the digest-pinned sandbox image (EXEC_BACKEND=docker)
# that production uses. Requires Docker running and EXEC_CONTAINER_IMAGE in .env.
set -euo pipefail

cd "$(dirname "$0")/.."

image="$(grep -E '^EXEC_CONTAINER_IMAGE=' .env | cut -d= -f2- || true)"
if [[ -z "$image" ]]; then
  echo "EXEC_CONTAINER_IMAGE is not set in .env; the release check needs the pinned sandbox image." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker is not running; start Docker Desktop and re-run." >&2
  exit 1
fi

echo "Backend suite on the pinned sandbox image (${image:0:19}...)"
EXEC_BACKEND=docker EXEC_CONTAINER_IMAGE="$image" \
  .venv/bin/python -m pytest -q -rs -p no:cacheprovider \
  --deselect tests/test_reference_maintenance.py::test_framework_sections_are_stable_and_exclude_labs

echo "Release check passed."
