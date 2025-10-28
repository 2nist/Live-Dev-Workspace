"""
Arranger OSC server for API and Live integration.

Handles OSC messages for arrangement control, theory guidance, and Live operations.
"""
import json
from pythonosc.dispatcher import Dispatcher
from pythonosc.osc_server import ThreadingOSCUDPServer
from pythonosc import udp_client
from arranger.api import theory, live_integration, analysis
from arranger.live_bridge.live_bridge import SceneManager, ChordClipFactory, PlaybackScheduler
from arranger.live_bridge.ableton_connection import AbletonConnection

class ArrangerOSCServer:
    def __init__(self, ip="127.0.0.1", port=12000, reply_port=12001, 
                 ableton_host="127.0.0.1", ableton_port=11000, use_live=False):
        self.dispatcher = Dispatcher()
        self.server = ThreadingOSCUDPServer((ip, port), self.dispatcher)
        self.client = udp_client.SimpleUDPClient(ip, reply_port)
        
        # Initialize Ableton connection if requested
        if use_live:
            self.ableton = AbletonConnection(ableton_host, ableton_port)
        else:
            self.ableton = AbletonConnection(mock=True)
        
        # Initialize Live bridge components with connection
        self.scene_manager = SceneManager(self.ableton)
        self.clip_factory = ChordClipFactory(self.ableton)
        self.playback_scheduler = PlaybackScheduler(self.ableton)
        self._register_handlers()

    def _register_handlers(self):
        # Theory guidance
        self.dispatcher.map("/theory/guidance", self.handle_theory_guidance)
        self.dispatcher.map("/theory/progressions", self.handle_progressions)
        self.dispatcher.map("/theory/cadences", self.handle_cadences)
        self.dispatcher.map("/theory/analyze_arrangement", self.handle_analyze_arrangement)
        # Live integration
        self.dispatcher.map("/live/theory_suggestions", self.handle_live_theory_suggestions)
        # Scene and clip management
        self.dispatcher.map("/live/create_scene", self.handle_create_scene)
        self.dispatcher.map("/live/create_chord_clip", self.handle_create_chord_clip)
        self.dispatcher.map("/live/schedule_playback", self.handle_schedule_playback)


    def handle_theory_guidance(self, address, *args):
        # Expect: /theory/guidance <key> <mode> <chord>
        context = {}
        if len(args) >= 3:
            context = {"key": args[0], "mode": args[1], "chord": args[2]}
        result = theory.api_get_theory_guidance(context)
        self._send_reply(address, result)

    def handle_progressions(self, address, key, mode):
        result = theory.api_get_progressions(key, mode)
        self._send_reply(address, result)

    def handle_cadences(self, address):
        result = theory.api_get_cadences()
        self._send_reply(address, result)

    def handle_analyze_arrangement(self, address, *args):
        # Expect: /theory/analyze_arrangement <arrangement_json>
        arrangement = {}
        if args:
            # Parse JSON string if provided
            try:
                arrangement = json.loads(args[0]) if isinstance(args[0], str) else args[0]
            except (json.JSONDecodeError, IndexError):
                arrangement = {}
        result = analysis.analyze_arrangement(arrangement)
        self._send_reply(address, result)

    def handle_live_theory_suggestions(self, address, *args):
        # Expect: /live/theory_suggestions <live_state_json>
        live_state = {}
        if args:
            # Parse JSON string if provided
            try:
                live_state = json.loads(args[0]) if isinstance(args[0], str) else args[0]
            except (json.JSONDecodeError, IndexError):
                live_state = {}
        result = live_integration.live_theory_suggestions(live_state)
        self._send_reply(address, result)

    def handle_create_scene(self, address, name, *clips):
        """Create a scene in Live via SceneManager."""
        clips_list = [clip for clip in clips]  # Convert args to list
        self.scene_manager.create_scene(name, clips_list)
        self._send_reply(address, {"status": "scene created", "name": name})

    def handle_create_chord_clip(self, address, chord, length, track):
        """Create a chord MIDI clip via ChordClipFactory."""
        self.clip_factory.create_chord_clip(chord, length, track)
        self._send_reply(address, {"status": "clip created", "chord": chord})

    def handle_schedule_playback(self, address, *order):
        """Schedule playback via PlaybackScheduler."""
        order_list = list(order)
        self.playback_scheduler.schedule_playback(order_list)
        self._send_reply(address, {"status": "playback scheduled", "order": order_list})

    def _send_reply(self, address, result):
        """Send OSC reply to client."""
        # Convert result to OSC-compatible format (strings/numbers)
        reply_address = f"{address}/reply"
        self.client.send_message(reply_address, str(result))
        print(f"OSC reply to {reply_address}: {result}")

    def serve_forever(self):
        print(f"Arranger OSC server running on {self.server.server_address}")
        self.server.serve_forever()

# To run:
# server = ArrangerOSCServer()
# server.serve_forever()
