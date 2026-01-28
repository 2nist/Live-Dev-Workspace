#!/bin/bash
# Helper script to run metadata analysis with correct Python

cd "$(dirname "$0")"

# Use pyenv Python
PYTHON="/Users/Matthew/.pyenv/versions/3.8.19/bin/python3"

# Check if jams is installed
$PYTHON -c "import jams" 2>/dev/null || {
    echo "Installing jams library..."
    $PYTHON -m pip install --user jams
}

# Run analysis
echo "Running metadata analysis..."
echo ""

$PYTHON choco_metadata_analysis.py \
    --jams-dir /Users/Matthew/Choco/choco-main/partitions \
    --sample 100 \
    --output quick_report.txt

echo ""
echo "Report saved to: quick_report.txt"
