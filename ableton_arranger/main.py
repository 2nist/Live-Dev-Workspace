#!/usr/bin/env python3
"""
Ableton Arranger - Main entry point.
Section-based arrangement helper for Ableton Live.
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add workspace root directory to path for imports
# main.py is in ableton_arranger/, so we need the parent directory
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

from ableton_arranger.gui.main_window import MainWindow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setApplicationName("Ableton Arranger")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = MainWindow()
    window.show()
    
    logger.info("Ableton Arranger started")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
