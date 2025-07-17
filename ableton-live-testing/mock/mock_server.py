#!/usr/bin/env python3
"""
LATE Mock Server

Simulates Ableton Live API responses for fast, isolated unit tests.
"""
from flask import Flask, request, jsonify
import time

app = Flask(__name__)

@app.route('/api/get_session_info', methods=['GET'])
def get_session_info():
    return jsonify({"session": "Mock Session Info", "status": "ok"})

@app.route('/api/create_midi_track', methods=['POST'])
def create_midi_track():
    data = request.get_json()
    return jsonify({"result": f"Mock MIDI track created at index {data.get('index', -1)}", "status": "ok"})

@app.route('/api/set_tempo', methods=['POST'])
def set_tempo():
    data = request.get_json()
    return jsonify({"result": f"Mock tempo set to {data.get('tempo', 120)} BPM", "status": "ok"})

if __name__ == '__main__':
    print("Starting LATE Mock Server on http://localhost:9877 ...")
    app.run(port=9877)
