#!/usr/bin/env python3
"""
Example: Using the integrated Ableton Arranger application.

This demonstrates the complete workflow:
1. Analyze an audio file
2. Import analysis into sections
3. Edit chord progressions
4. Build arrangement in Ableton Live
"""
import sys
import os

# Add workspace root to path
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from ableton_arranger.gui.integrated_main_window import IntegratedMainWindow


def main():
    """Run the integrated application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Ableton Arranger - Integrated")
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = IntegratedMainWindow()
    window.show()
    
    print("Integrated Ableton Arranger started")
    print("Features:")
    print("  - 4-panel layout: Sections | Chords | Analyzer | Data Browser")
    print("  - Audio analysis with structure detection")
    print("  - Chord progression editing")
    print("  - Song library management")
    print("  - Project management")
    print("  - Ableton Live integration via OSC")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
