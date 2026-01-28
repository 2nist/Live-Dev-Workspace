#!/bin/bash
# Quick script to check analysis progress

cd "$(dirname "$0")"

if [ -f "analysis_progress.log" ]; then
    echo "=== Analysis Progress ==="
    tail -20 analysis_progress.log
    echo ""
    echo "=== File Count ==="
    if [ -f "full_metadata_data.json" ]; then
        echo "✓ Analysis complete! JSON file exists."
        python3 -c "import json; data=json.load(open('full_metadata_data.json')); print(f\"Total files analyzed: {data['statistics']['total_files']}\")" 2>/dev/null || echo "Checking file..."
    else
        echo "Analysis still running..."
    fi
else
    echo "Analysis not started or log file not found."
fi

if [ -f "full_metadata_report.txt" ]; then
    echo ""
    echo "=== Report Summary ==="
    grep -A 15 "Overall Coverage:" full_metadata_report.txt | head -20
fi
