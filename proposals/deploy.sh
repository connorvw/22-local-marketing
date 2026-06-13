#!/usr/bin/env bash
# Deploy ALL proposals in site/ to Cloudflare Pages (project: 22lm-proposals).
# Validates every proposal's JS first; aborts if any fail.
# Usage:  bash deploy.sh
set -uo pipefail
cd "$(dirname "$0")"

export CLOUDFLARE_ACCOUNT_ID="ff4bcfdaf56c61c138988bc01d894d84"
# CLOUDFLARE_API_TOKEN is expected in the environment (it is, per the agent shell).

echo "== Validating every proposal in site/ =="
fail=0
for f in site/*/index.html; do
  [ -e "$f" ] || continue
  if ! python validate.py "$f" >/tmp/vout 2>&1; then
    echo "FAIL  $f"
    cat /tmp/vout
    fail=1
  else
    echo "ok    $f"
  fi
done
if [ "$fail" = 1 ]; then
  echo ""
  echo "Aborting deploy. A JS syntax error breaks the whole page. Fix the above first."
  exit 1
fi

echo ""
echo "== Deploying site/ to 22lm-proposals =="
npx wrangler pages deploy site --project-name=22lm-proposals --branch=main --commit-dirty=true

echo ""
echo "Live at: https://proposals.22localmarketing.com/{slug}/  (and 22lm-proposals.pages.dev/{slug}/)"
