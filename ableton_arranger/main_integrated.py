#!/usr/bin/env python3
"""
Ableton Arranger - Integrated Main Entry Point.
Complete application with 4-panel layout: Sections | Chords | Analyzer | Data Browser
"""
import sys
import os
import logging
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt

# Add workspace root directory to path for imports
workspace_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, workspace_root)

from ableton_arranger.gui.integrated_main_window import IntegratedMainWindow


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def main():
    """Main entry point for integrated application."""
    app = QApplication(sys.argv)
    app.setApplicationName("Ableton Arranger - Integrated")
    
    # Enable high DPI scaling
    app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    
    window = IntegratedMainWindow()
    window.show()
    
    logger.info("Ableton Arranger (Integrated) started")
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
