#!/usr/bin/env bash
# Constraint-12 secret-scan: gates git commit against staged-diff leaks.
# Modes:
#   - Hook: invoked by PreToolUse with JSON on stdin, gates only `git commit`.
#   - Standalone: run directly to scan current staged diff.
# Patterns cover the mission's minimum set: API keys, GitHub tokens, AWS keys,
# Slack tokens, private keys, JWT_SECRET, service-account JSON, embedded URL creds.

set -uo pipefail

PATTERNS_FILE=$(mktemp)
trap 'rm -f "$PATTERNS_FILE"' EXIT

cat >"$PATTERNS_FILE" <<'EOF'
sk-[A-Za-z0-9]{20,}
ghp_[A-Za-z0-9]{20,}
gho_[A-Za-z0-9]{20,}
ghs_[A-Za-z0-9]{20,}
github_pat_[A-Za-z0-9_]{20,}
AKIA[0-9A-Z]{16}
xox[abprs]-[A-Za-z0-9-]{10,}
BEGIN (RSA|OPENSSH|EC|DSA|PGP|ENCRYPTED) PRIVATE KEY
JWT_SECRET=[A-Za-z0-9+/=_-]{8,}
"private_key"[[:space:]]*:
"type"[[:space:]]*:[[:space:]]*"service_account"
://[A-Za-z0-9._%-]+:[^@[:space:]<>"']+@[A-Za-z0-9.-]+
OPENFDA_API_KEY=[A-Za-z0-9]{20,}
EOF

IS_HOOK=0
if [ ! -t 0 ]; then
  IS_HOOK=1
  STDIN_JSON=$(cat)
  TOOL_NAME=$(echo "$STDIN_JSON" | python3 -c 'import sys,json
try:
  d=json.load(sys.stdin); print(d.get("tool_name",""))
except Exception:
  print("")' 2>/dev/null || echo "")
  CMD=$(echo "$STDIN_JSON" | python3 -c 'import sys,json
try:
  d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command",""))
except Exception:
  print("")' 2>/dev/null || echo "")
  # Only act on git commit calls
  if [ "$TOOL_NAME" != "Bash" ]; then exit 0; fi
  if ! echo "$CMD" | grep -qE '(^|[ ;|&])git( -[^ ]+)* commit\b'; then exit 0; fi
fi

# Identify repo root for the staged diff (if inside a repo)
if ! git rev-parse --show-toplevel >/dev/null 2>&1; then
  exit 0
fi

DIFF=$(git diff --cached -U0 2>/dev/null || true)
if [ -z "$DIFF" ]; then exit 0; fi

# Look only at added lines (lines beginning with + that are not the +++ header)
ADDED=$(echo "$DIFF" | grep -E '^\+' | grep -vE '^\+\+\+' || true)
if [ -z "$ADDED" ]; then exit 0; fi

FOUND=0
while IFS= read -r pat; do
  [ -z "$pat" ] && continue
  HITS=$(echo "$ADDED" | grep -EnH "$pat" 2>/dev/null | head -5 || true)
  if [ -n "$HITS" ]; then
    echo "[secret-scan] FORBIDDEN PATTERN: $pat" >&2
    echo "$HITS" >&2
    FOUND=1
  fi
done <"$PATTERNS_FILE"

if [ $FOUND -ne 0 ]; then
  echo "[secret-scan] Blocking commit per mission constraint 12. Redact and re-stage." >&2
  exit 2
fi

exit 0
