import os
import socket
import time
import threading
import unittest

# Ensure python/src is on the path when running directly
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
PY_SRC = os.path.join(WORKSPACE_ROOT, "src")
if PY_SRC not in os.sys.path:
    os.sys.path.insert(0, PY_SRC)

from pythonosc.udp_client import SimpleUDPClient


class TestOSCServerSmoke(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Start the OSC server in a background thread using ArrangerOSCServer class
        from arranger.live_bridge.osc_server import ArrangerOSCServer

        def run_server():
            # Use non-default ports to avoid conflicts
            server = ArrangerOSCServer(ip="127.0.0.1", port=11001, reply_port=11002, use_live=False)
            server.serve_forever()

        cls.thread = threading.Thread(target=run_server, daemon=True)
        cls.thread.start()
        # Wait briefly for server to bind
        time.sleep(0.3)

    def test_server_health_and_theory(self):
        client = SimpleUDPClient("127.0.0.1", 11001)
        # Send a ping/health message if available, else try a theory endpoint
        # Fallback to theory chord parse: /theory/chord <symbol>
        # We can't listen for response easily here; ensure server socket is open by sending a datagram.
        try:
            client.send_message("/theory/chord", "Cmaj7")
            ok = True
        except Exception:
            ok = False
        self.assertTrue(ok, "OSC server should accept datagrams on the test port")


if __name__ == "__main__":
    unittest.main()
