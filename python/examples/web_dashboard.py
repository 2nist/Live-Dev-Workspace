"""
Flask web dashboard for Arranger OSC server.

Provides a browser-based UI to monitor and control Ableton Live via the arranger system.
"""
import os
import time
from flask import Flask, render_template, jsonify, request
from flask_cors import CORS
from pythonosc.udp_client import SimpleUDPClient
from pythonosc.osc_server import BlockingOSCUDPServer
from pythonosc.dispatcher import Dispatcher
import threading

app = Flask(__name__)
CORS(app)

# OSC client to send to arranger server
ARRANGER_IP = os.getenv("ARRANGER_OSC_IP", "127.0.0.1")
ARRANGER_PORT = int(os.getenv("ARRANGER_OSC_PORT", "12000"))
DASHBOARD_REPLY_PORT = 13000  # Listen for replies on separate port

osc_client = SimpleUDPClient(ARRANGER_IP, ARRANGER_PORT)

# State cache (updated from OSC replies)
live_state = {
    "tempo": 120.0,
    "playing": False,
    "time_signature": [4, 4],
    "scenes": [],
    "num_tracks": 0,
    "last_reply": "",
    "connected": False
}

# OSC reply listener
dispatcher = Dispatcher()

def handle_reply(address, *args):
    """Handle incoming OSC replies from arranger server."""
    global live_state
    live_state["last_reply"] = f"{address}: {args}"
    
    # Parse specific reply types
    if "tempo" in address:
        if args and isinstance(args[0], (int, float)):
            live_state["tempo"] = float(args[0])
        elif args and isinstance(args[0], str):
            # Parse dict string if needed
            try:
                import ast
                data = ast.literal_eval(args[0])
                if "tempo" in data:
                    live_state["tempo"] = data["tempo"]
            except:
                pass
    
    if "playing" in address or "status" in address:
        if args and "playing" in str(args[0]).lower():
            live_state["playing"] = True
        elif args and "stopped" in str(args[0]).lower():
            live_state["playing"] = False

dispatcher.set_default_handler(handle_reply)

def run_osc_listener():
    """Run OSC server to receive replies in background thread."""
    server = BlockingOSCUDPServer(("127.0.0.1", DASHBOARD_REPLY_PORT), dispatcher)
    print(f"Dashboard OSC listener on port {DASHBOARD_REPLY_PORT}")
    server.serve_forever()

# Start listener thread
listener_thread = threading.Thread(target=run_osc_listener, daemon=True)
listener_thread.start()

@app.route('/')
def index():
    """Render main dashboard page."""
    return render_template('dashboard.html')

@app.route('/api/state')
def get_state():
    """Get current Live state."""
    return jsonify(live_state)

@app.route('/api/play', methods=['POST'])
def play():
    """Start playback."""
    osc_client.send_message("/live/play", [])
    live_state["playing"] = True
    return jsonify({"status": "playing"})

@app.route('/api/stop', methods=['POST'])
def stop():
    """Stop playback."""
    osc_client.send_message("/live/stop", [])
    live_state["playing"] = False
    return jsonify({"status": "stopped"})

@app.route('/api/tempo', methods=['POST'])
def set_tempo():
    """Set tempo."""
    data = request.get_json()
    tempo = float(data.get('tempo', 120))
    osc_client.send_message("/live/set_tempo", tempo)
    live_state["tempo"] = tempo
    return jsonify({"tempo": tempo})

@app.route('/api/scene/create', methods=['POST'])
def create_scene():
    """Create a new scene."""
    osc_client.send_message("/live/create_scene_index", -1)
    return jsonify({"status": "scene created"})

@app.route('/api/scene/trigger/<int:index>', methods=['POST'])
def trigger_scene(index):
    """Trigger a scene."""
    osc_client.send_message("/live/trigger_scene", index)
    return jsonify({"status": f"triggered scene {index}"})

@app.route('/api/clip/create', methods=['POST'])
def create_clip():
    """Create a MIDI clip."""
    data = request.get_json()
    track = int(data.get('track', 0))
    scene = int(data.get('scene', 0))
    length = float(data.get('length', 4.0))
    osc_client.send_message("/live/clip/create", [track, scene, length])
    return jsonify({"status": "clip created"})

@app.route('/api/track/volume', methods=['POST'])
def set_volume():
    """Set track volume."""
    data = request.get_json()
    track = int(data.get('track', 0))
    volume = float(data.get('volume', 0.85))
    osc_client.send_message("/live/track/set/volume", [track, volume])
    return jsonify({"track": track, "volume": volume})

if __name__ == '__main__':
    print(f"Arranger Dashboard starting on http://localhost:5000")
    print(f"OSC target: {ARRANGER_IP}:{ARRANGER_PORT}")
    app.run(debug=True, host='127.0.0.1', port=5000, use_reloader=False)
