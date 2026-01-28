#!/bin/bash
# Run analysis with progress monitoring

cd "$(dirname "$0")"

PYTHON="/Users/Matthew/.pyenv/versions/3.8.19/bin/python3"
JAMS_DIR="/Users/Matthew/Choco/choco-main/partitions"

echo "Starting metadata analysis..."
echo "Total JAMS files: $(find "$JAMS_DIR" -name "*.jams" -type f 2>/dev/null | wc -l | tr -d ' ')"
echo ""
echo "This will take a while for the full dataset."
echo "Progress will be saved to: analysis_progress.log"
echo ""

# Run analysis in background and show progress
$PYTHON choco_metadata_analysis.py \
    --jams-dir "$JAMS_DIR" \
    --output full_metadata_report.txt \
    --json full_metadata_data.json \
    2>&1 | grep -v "UserWarning\|Failed validating\|On instance" | tee analysis_progress.log &

ANALYSIS_PID=$!

echo "Analysis started (PID: $ANALYSIS_PID)"
echo "Monitor progress with: tail -f analysis_progress.log"
echo "Or run: ./check_analysis_status.sh"
echo ""
echo "To stop: kill $ANALYSIS_PID"
