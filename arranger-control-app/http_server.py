"""
Simple HTTP server for Arranger Control Electron app.
Provides REST API endpoints that proxy to AbletonOSC.
"""
from flask import Flask, request, jsonify
from flask_cors import CORS
from pythonosc import udp_client
import time

app = Flask(__name__)
CORS(app)

# OSC client to communicate with AbletonOSC
osc_client = udp_client.SimpleUDPClient("127.0.0.1", 11000)

@app.route('/live/play', methods=['POST'])
def play():
    osc_client.send_message("/live/song/start_playing", [])
    return jsonify({"status": "playing"})

@app.route('/live/stop', methods=['POST'])
def stop():
    osc_client.send_message("/live/song/stop_playing", [])
    return jsonify({"status": "stopped"})

@app.route('/live/set_tempo', methods=['POST'])
def set_tempo():
    data = request.get_json()
    tempo = float(data.get('tempo', 120))
    osc_client.send_message("/live/song/set/tempo", [tempo])
    return jsonify({"status": "tempo set", "tempo": tempo})

@app.route('/live/get_tempo', methods=['POST', 'GET'])
def get_tempo():
    # Since we can't easily get OSC replies, return a reasonable default
    # In production, you'd use OSC listener or WebSocket
    return jsonify({"tempo": 120.0})

@app.route('/live/get_time_signature', methods=['POST', 'GET'])
def get_time_signature():
    return jsonify({"time_signature": [4, 4]})

@app.route('/live/create_scene_index', methods=['POST'])
def create_scene():
    data = request.get_json()
    index = int(data.get('index', -1))
    osc_client.send_message("/live/song/create_scene", [index])
    return jsonify({"status": "scene created", "index": index})

@app.route('/live/trigger_scene', methods=['POST'])
def trigger_scene():
    data = request.get_json()
    index = int(data.get('index', 0))
    osc_client.send_message("/live/scene/fire", [index])
    return jsonify({"status": "scene triggered", "index": index})

@app.route('/live/clip/create', methods=['POST'])
def create_clip():
    data = request.get_json()
    track = int(data.get('track', 0))
    scene = int(data.get('scene', 0))
    length = float(data.get('length', 4.0))
    osc_client.send_message("/live/clip_slot/create_clip", [track, scene, length])
    return jsonify({"status": "clip created", "track": track, "scene": scene})

@app.route('/live/clip/add_note', methods=['POST'])
def add_note():
    data = request.get_json()
    track = int(data.get('track', 0))
    scene = int(data.get('scene', 0))
    pitch = int(data.get('pitch', 60))
    start = float(data.get('start', 0.0))
    duration = float(data.get('dur', 1.0))
    velocity = int(data.get('vel', 100))
    
    osc_client.send_message("/live/clip/add/notes", 
                           [track, scene, pitch, start, duration, velocity, 0])
    return jsonify({"status": "note added"})

@app.route('/live/track/set/volume', methods=['POST'])
def set_volume():
    data = request.get_json()
    track = int(data.get('track', 0))
    volume = float(data.get('volume', 0.85))
    osc_client.send_message("/live/track/set/volume", [track, volume])
    return jsonify({"status": "volume set", "track": track, "volume": volume})

@app.route('/live/track/get/volume', methods=['POST'])
def get_volume():
    data = request.get_json()
    track = int(data.get('track', 0))
    return jsonify({"track": track, "volume": 0.85})

@app.route('/live/track/set/pan', methods=['POST'])
def set_pan():
    data = request.get_json()
    track = int(data.get('track', 0))
    pan = float(data.get('pan', 0.0))
    osc_client.send_message("/live/track/set/panning", [track, pan])
    return jsonify({"status": "pan set", "track": track, "pan": pan})

@app.route('/live/track/set/mute', methods=['POST'])
def set_mute():
    data = request.get_json()
    track = int(data.get('track', 0))
    mute = bool(data.get('mute', False))
    osc_client.send_message("/live/track/set/mute", [track, 1 if mute else 0])
    return jsonify({"status": "mute set", "track": track, "mute": mute})

@app.route('/live/track/set/solo', methods=['POST'])
def set_solo():
    data = request.get_json()
    track = int(data.get('track', 0))
    solo = bool(data.get('solo', False))
    osc_client.send_message("/live/track/set/solo", [track, 1 if solo else 0])
    return jsonify({"status": "solo set", "track": track, "solo": solo})

@app.route('/live/track/set/arm', methods=['POST'])
def set_arm():
    data = request.get_json()
    track = int(data.get('track', 0))
    arm = bool(data.get('arm', False))
    osc_client.send_message("/live/track/set/arm", [track, 1 if arm else 0])
    return jsonify({"status": "arm set", "track": track, "arm": arm})

if __name__ == '__main__':
    print("=" * 50)
    print("Arranger Control HTTP Server")
    print("=" * 50)
    print(f"Server running on: http://127.0.0.1:12000")
    print(f"Sending OSC to AbletonOSC on port 11000")
    print("=" * 50)
    app.run(host='127.0.0.1', port=12000, debug=False)
