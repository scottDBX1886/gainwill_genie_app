#!/usr/bin/env bash
# Build, deploy, and run the Gainwell Genie app.
# Usage: ./build-deploy-run.sh [target] [profile]
# Example: ./build-deploy-run.sh dev dbx_shared_demo

set -e

TARGET="${1:-dev}"
PROFILE="${2:-dbx_shared_demo}"
ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "=== Build ==="
cd "$ROOT/src/app"
uv run apx build

echo ""
echo "=== Deploy (target=$TARGET, profile=$PROFILE) ==="
cd "$ROOT"
databricks bundle deploy -t "$TARGET" --profile "$PROFILE"

echo ""
echo "=== Run app ==="
databricks bundle run gainwell_genie_app -t "$TARGET" --profile "$PROFILE"

echo ""
echo "Done. Open the URL above to use the app."
