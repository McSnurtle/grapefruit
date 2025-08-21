#!/bin/bash

echo "Running grapefruit"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# python venv
source ./venv/bin/activate
python src/ui.py
deactivate

read -p "Press enter to continue..."
