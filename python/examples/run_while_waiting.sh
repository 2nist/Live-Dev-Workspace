#!/bin/bash
# Run other tasks while main pipeline is processing

cd "$(dirname "$0")"
PYTHON="/Users/Matthew/.pyenv/versions/3.8.19/bin/python3"

echo "=== What would you like to do while the pipeline runs? ==="
echo ""
echo "1. Check pipeline status"
echo "2. Test on a small sample dataset"
echo "3. Run metadata analysis on a subset"
echo "4. Test chord conversion"
echo "5. Search existing enhanced files"
echo "6. View pipeline progress live"
echo ""

read -p "Enter choice (1-6): " choice

case $choice in
    1)
        ./check_pipeline.sh
        ;;
    2)
        echo "Running test on isophonics dataset..."
        $PYTHON choco_enhancement_pipeline.py \
            --jams-dir /Users/Matthew/Choco/choco-main/partitions/isophonics \
            --output-dir ./choco_enhanced_test
        ;;
    3)
        echo "Running metadata analysis on sample..."
        $PYTHON choco_metadata_analysis.py \
            --jams-dir /Users/Matthew/Choco/choco-main/partitions/isophonics \
            --output isophonics_report.txt
        cat isophonics_report.txt
        ;;
    4)
        echo "Testing chord conversion..."
        $PYTHON -c "
from sys import path
path.insert(0, '../src')
from choco_integration import harte_to_midi_notes
chords = ['C:maj7', 'F:min', 'G:dom7', 'A:min']
for chord in chords:
    notes = harte_to_midi_notes(chord)
    print(f'{chord} -> MIDI notes: {notes}')
"
        ;;
    5)
        if [ -d "./choco_enhanced/json_enhanced" ]; then
            echo "Searching enhanced files..."
            $PYTHON choco_search_example.py \
                --enhanced-dir ./choco_enhanced/json_enhanced \
                --filter-genre jazz \
                --limit 10
        else
            echo "Enhanced files not ready yet. Run option 2 first."
        fi
        ;;
    6)
        echo "Watching pipeline progress (Ctrl+C to stop)..."
        tail -f pipeline.log
        ;;
    *)
        echo "Invalid choice"
        ;;
esac
