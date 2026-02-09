#!/bin/bash
#
# Quick launcher for macOS (development mode)
#
# This script launches the app directly from source without building.
# Useful for testing changes quickly without rebuilding.
#

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Activate virtual environment if it exists
if [[ -d "$SCRIPT_DIR/venv" ]]; then
    source "$SCRIPT_DIR/venv/bin/activate"
fi

# Launch the app
echo "Launching Choke Test Safety Check..."
python3 "$SCRIPT_DIR/run.py" "$@"
