#!/usr/bin/env python3
"""
Unified Entry Point for Ableton Arranger.

Main entry point that can run in different modes:
- GUI mode (default): PyQt5 application
- OSC server mode: Run OSC server for Max for Live integration
- API server mode: Run FastAPI server
"""

import sys
import os
import argparse
import logging

# Add python/src to path
workspace_root = os.path.dirname(os.path.abspath(__file__))
python_src = os.path.join(workspace_root, "Live-Dev-Workspace", "python", "src")
if python_src not in sys.path:
    sys.path.insert(0, python_src)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def run_gui():
    """Run the PyQt5 GUI application."""
    try:
        from PyQt5.QtWidgets import QApplication
        from PyQt5.QtCore import Qt
        from ableton_arranger.gui.main_window import MainWindow
        
        app = QApplication(sys.argv)
        app.setApplicationName("Ableton Arranger")
        
        # Enable high DPI scaling
        app.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        app.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
        
        window = MainWindow()
        window.show()
        
        logger.info("Ableton Arranger GUI started")
        sys.exit(app.exec_())
    except ImportError as e:
        logger.error(f"Failed to import GUI components: {e}")
        logger.error("Make sure PyQt5 is installed: pip install PyQt5")
        sys.exit(1)


def run_osc_server(ip="127.0.0.1", port=12000, reply_port=12001, 
                   live_host="127.0.0.1", live_port=11000, use_live=False):
    """Run the OSC server."""
    try:
        from arranger.live_bridge.osc_server import ArrangerOSCServer
        
        logger.info(f"Starting OSC server on {ip}:{port}")
        server = ArrangerOSCServer(
            ip=ip,
            port=port,
            reply_port=reply_port,
            ableton_host=live_host,
            ableton_port=live_port,
            use_live=use_live
        )
        server.serve_forever()
    except Exception as e:
        logger.error(f"Failed to start OSC server: {e}")
        sys.exit(1)


def run_api_server(host="127.0.0.1", port=8000):
    """Run the FastAPI server."""
    try:
        import uvicorn
        from arranger.api.server import app
        
        logger.info(f"Starting FastAPI server on {host}:{port}")
        uvicorn.run(app, host=host, port=port)
    except ImportError:
        logger.error("FastAPI/uvicorn not installed: pip install fastapi uvicorn")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Failed to start API server: {e}")
        sys.exit(1)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Ableton Arranger - Unified entry point",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run GUI (default)
  python arranger_main.py
  
  # Run OSC server
  python arranger_main.py --mode osc
  
  # Run API server
  python arranger_main.py --mode api
  
  # Run OSC server with Live connection
  python arranger_main.py --mode osc --use-live
        """
    )
    
    parser.add_argument(
        "--mode",
        choices=["gui", "osc", "api"],
        default="gui",
        help="Run mode: gui (default), osc (OSC server), or api (FastAPI server)"
    )
    
    # OSC server options
    parser.add_argument("--ip", default="127.0.0.1", help="OSC server IP (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=12000, help="OSC server port (default: 12000)")
    parser.add_argument("--reply", type=int, default=12001, help="OSC reply port (default: 12001)")
    parser.add_argument("--live-host", default="127.0.0.1", help="AbletonOSC host (default: 127.0.0.1)")
    parser.add_argument("--live-port", type=int, default=11000, help="AbletonOSC port (default: 11000)")
    parser.add_argument("--use-live", action="store_true", help="Connect to Ableton Live")
    
    # API server options
    parser.add_argument("--api-host", default="127.0.0.1", help="API server host (default: 127.0.0.1)")
    parser.add_argument("--api-port", type=int, default=8000, help="API server port (default: 8000)")
    
    args = parser.parse_args()
    
    if args.mode == "gui":
        run_gui()
    elif args.mode == "osc":
        run_osc_server(
            ip=args.ip,
            port=args.port,
            reply_port=args.reply,
            live_host=args.live_host,
            live_port=args.live_port,
            use_live=args.use_live
        )
    elif args.mode == "api":
        run_api_server(host=args.api_host, port=args.api_port)


if __name__ == "__main__":
    main()
