#!/bin/bash

echo "Running installation for https://github.com/McSnurtle/gbro.git"

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.." || exit 1

# python installations
echo "Using $(python3 --version)"
python3 -m venv venv
source ./venv/bin/activate
echo "Upgrading dependencies..."
pip install --upgrade --verbose -r requirements.txt
deactivate

read -p "Press enter to continue..."

