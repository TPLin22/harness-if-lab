#!/bin/bash
set -euo pipefail

cd /testbed
python - <<'PY'
from app import normalize_name

assert normalize_name("  Ada Lovelace  ") == "Ada Lovelace"
PY

mkdir -p /logs/verifier
printf '1\n' > /logs/verifier/reward.txt
