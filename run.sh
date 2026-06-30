#!/bin/bash
# Get the absolute directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd )"

cd "$DIR"

# Activate the virtual environment
source venv/bin/activate

# Run the voice typing script
python main.py
