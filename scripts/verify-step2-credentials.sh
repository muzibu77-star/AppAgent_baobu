#!/usr/bin/env bash
set -euo pipefail

CREDENTIALS_FILE="${1:-/home/tiger/.config/appagentx/credentials.env}"

if [[ ! -f "$CREDENTIALS_FILE" ]]; then
  echo "missing_credentials_file: $CREDENTIALS_FILE"
  exit 1
fi

PERM="$(stat -c '%a' "$CREDENTIALS_FILE")"
if [[ "$PERM" != "600" ]]; then
  echo "bad_permissions: $PERM expected 600"
  exit 1
fi

set -a
# shellcheck disable=SC1090
. "$CREDENTIALS_FILE"
set +a

python3 - <<'PY'
import os
import sys

required = [
    "APPAGENTX_LLM_BASE_URL",
    "APPAGENTX_LLM_MODEL",
    "APPAGENTX_LLM_API_KEY",
    "APPAGENTX_NEO4J_URI",
    "APPAGENTX_NEO4J_USERNAME",
    "APPAGENTX_NEO4J_PASSWORD",
    "APPAGENTX_PINECONE_API_KEY",
    "APPAGENTX_PINECONE_PROJECT",
    "APPAGENTX_PINECONE_REGION",
]

missing = [name for name in required if not os.environ.get(name)]
if missing:
    print("missing:", ",".join(missing))
    sys.exit(1)

llm_base_url_ok = os.environ["APPAGENTX_LLM_BASE_URL"].startswith("https://")
neo4j_uri_ok = os.environ["APPAGENTX_NEO4J_URI"].startswith(
    ("neo4j://", "neo4j+s://", "bolt://", "bolt+s://")
)
pinecone_region = os.environ["APPAGENTX_PINECONE_REGION"]

print("credentials_fields_ok")
print("llm_base_url_ok", llm_base_url_ok)
print("neo4j_uri_ok", neo4j_uri_ok)
print("pinecone_region", pinecone_region)

if not llm_base_url_ok or not neo4j_uri_ok:
    sys.exit(1)
PY

python3 - <<'PY'
from pathlib import Path
import sys

repo = Path("/home/tiger/BaoBuu/AppAgent_baobu").resolve()
secret = Path("/home/tiger/.config/appagentx/credentials.env").resolve()

if repo == secret or repo in secret.parents:
    print("secret_inside_repo")
    sys.exit(1)

print("secret_outside_repo_ok")
PY
