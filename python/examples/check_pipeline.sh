#!/bin/bash
# Quick script to check pipeline progress

cd "$(dirname "$0")"

echo "=== Pipeline Status ==="
if ps aux | grep -q "[c]hoco_enhancement_pipeline"; then
    echo "✓ Pipeline is RUNNING"
    ps aux | grep "[c]hoco_enhancement_pipeline" | awk '{print "  PID:", $2, "CPU:", $3"%", "Memory:", $4"%"}'
else
    echo "✗ Pipeline is NOT running"
fi

echo ""
echo "=== Progress Log (last 20 lines) ==="
if [ -f pipeline.log ]; then
    tail -20 pipeline.log
else
    echo "Log file not found yet"
fi

echo ""
echo "=== Output Files ==="
if [ -d "./choco_enhanced/json_intermediate" ]; then
    INTERMEDIATE=$(find ./choco_enhanced/json_intermediate -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  JSON intermediate: $INTERMEDIATE files"
else
    echo "  JSON intermediate: not started yet"
fi

if [ -d "./choco_enhanced/json_enhanced" ]; then
    ENHANCED=$(find ./choco_enhanced/json_enhanced -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
    echo "  JSON enhanced: $ENHANCED files"
else
    echo "  JSON enhanced: not started yet"
fi

if [ -d "./choco_enhanced/indexes" ]; then
    echo "  Indexes: created"
    ls -lh ./choco_enhanced/indexes/*.json 2>/dev/null | awk '{print "    -", $9, "(" $5 ")"}'
else
    echo "  Indexes: not created yet"
fi

echo ""
echo "Monitor in real-time: tail -f pipeline.log"
