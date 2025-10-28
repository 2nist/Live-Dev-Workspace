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
from arranger.hardware.hardware_bridge import get_hardware_bridge
from arranger.hardware.controller_manager import (
    get_controller_manager, 
    PushController, 
    LaunchpadController,
    APCController
)

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
        
        # Initialize hardware bridge
        self.hardware_bridge = get_hardware_bridge()
        self.controller_manager = get_controller_manager()
        
        self._register_handlers()

    def _register_handlers(self):
        # Theory guidance
        self.dispatcher.map("/theory/guidance", self.handle_theory_guidance)
        self.dispatcher.map("/theory/progressions", self.handle_progressions)
        self.dispatcher.map("/theory/cadences", self.handle_cadences)
        self.dispatcher.map("/theory/analyze_arrangement", self.handle_analyze_arrangement)
        # Live integration
        self.dispatcher.map("/live/theory_suggestions", self.handle_live_theory_suggestions)
        # Live transport
        self.dispatcher.map("/live/play", self.handle_live_play)
        self.dispatcher.map("/live/stop", self.handle_live_stop)
        self.dispatcher.map("/live/set_tempo", self.handle_live_set_tempo)
        self.dispatcher.map("/live/get_tempo", self.handle_live_get_tempo)
        self.dispatcher.map("/live/get_time_signature", self.handle_live_get_time_signature)
        # Scene and clip management
        self.dispatcher.map("/live/create_scene", self.handle_create_scene)
        self.dispatcher.map("/live/create_scene_index", self.handle_create_scene_index)
        self.dispatcher.map("/live/trigger_scene", self.handle_trigger_scene)
        self.dispatcher.map("/live/create_chord_clip", self.handle_create_chord_clip)
        self.dispatcher.map("/live/schedule_playback", self.handle_schedule_playback)
        # Track parameters
        self.dispatcher.map("/live/track/set/volume", self.handle_track_set_volume)
        self.dispatcher.map("/live/track/get/volume", self.handle_track_get_volume)
        self.dispatcher.map("/live/track/set/pan", self.handle_track_set_pan)
        self.dispatcher.map("/live/track/set/mute", self.handle_track_set_mute)
        self.dispatcher.map("/live/track/set/solo", self.handle_track_set_solo)
        self.dispatcher.map("/live/track/set/arm", self.handle_track_set_arm)
        # Clips (basic)
        self.dispatcher.map("/live/clip/create", self.handle_clip_create)
        self.dispatcher.map("/live/clip/add_note", self.handle_clip_add_note)
        
        # Hardware controller endpoints
        self.dispatcher.map("/hardware/detect", self.handle_detect_controllers)
        self.dispatcher.map("/hardware/list", self.handle_list_controllers)
        self.dispatcher.map("/hardware/connect", self.handle_connect_controller)
        self.dispatcher.map("/hardware/disconnect", self.handle_disconnect_controller)
        self.dispatcher.map("/hardware/set_mode", self.handle_set_mode)
        self.dispatcher.map("/hardware/display_progression", self.handle_display_progression)
        self.dispatcher.map("/hardware/display_arrangement", self.handle_display_arrangement)
        self.dispatcher.map("/hardware/highlight_chord", self.handle_highlight_chord)
        self.dispatcher.map("/hardware/highlight_section", self.handle_highlight_section)


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

    # Live transport handlers
    def handle_live_play(self, address):
        self.ableton.play()
        self._send_reply(address, {"status": "playing"})

    def handle_live_stop(self, address):
        self.ableton.stop()
        self._send_reply(address, {"status": "stopped"})

    def handle_live_set_tempo(self, address, tempo):
        try:
            self.ableton.set_tempo(float(tempo))
            self._send_reply(address, {"status": "tempo set", "tempo": float(tempo)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_live_get_tempo(self, address):
        try:
            tempo = self.ableton.get_tempo()
            self._send_reply(address, {"tempo": tempo})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_live_get_time_signature(self, address):
        try:
            ts = self.ableton.get_time_signature()
            self._send_reply(address, {"time_signature": ts})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_create_scene(self, address, name, *clips):
        """Create a scene in Live via SceneManager."""
        clips_list = [clip for clip in clips]  # Convert args to list
        self.scene_manager.create_scene(name, clips_list)
        self._send_reply(address, {"status": "scene created", "name": name})

    def handle_create_scene_index(self, address, index=-1):
        """Create a scene at a specific index using AbletonConnection directly."""
        try:
            idx = self.ableton.create_scene(int(index))
            self._send_reply(address, {"status": "scene created", "index": idx})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_trigger_scene(self, address, index):
        try:
            self.ableton.trigger_scene(int(index))
            self._send_reply(address, {"status": "scene triggered", "index": int(index)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_create_chord_clip(self, address, chord, length, track):
        """Create a chord MIDI clip via ChordClipFactory."""
        self.clip_factory.create_chord_clip(chord, length, track)
        self._send_reply(address, {"status": "clip created", "chord": chord})

    def handle_schedule_playback(self, address, *order):
        """Schedule playback via PlaybackScheduler."""
        order_list = list(order)
        self.playback_scheduler.schedule_playback(order_list)
        self._send_reply(address, {"status": "playback scheduled", "order": order_list})

    # Track parameter handlers
    def handle_track_set_volume(self, address, track, volume):
        try:
            self.ableton.set_track_volume(int(track), float(volume))
            self._send_reply(address, {"status": "volume set", "track": int(track), "volume": float(volume)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_track_get_volume(self, address, track):
        try:
            vol = self.ableton.get_track_volume(int(track))
            self._send_reply(address, {"track": int(track), "volume": float(vol)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_track_set_pan(self, address, track, pan):
        try:
            self.ableton.set_track_pan(int(track), float(pan))
            self._send_reply(address, {"status": "pan set", "track": int(track), "pan": float(pan)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_track_set_mute(self, address, track, mute):
        try:
            self.ableton.set_track_mute(int(track), bool(int(mute)))
            self._send_reply(address, {"status": "mute set", "track": int(track), "mute": bool(int(mute))})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_track_set_solo(self, address, track, solo):
        try:
            self.ableton.set_track_solo(int(track), bool(int(solo)))
            self._send_reply(address, {"status": "solo set", "track": int(track), "solo": bool(int(solo))})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_track_set_arm(self, address, track, arm):
        try:
            self.ableton.set_track_arm(int(track), bool(int(arm)))
            self._send_reply(address, {"status": "arm set", "track": int(track), "arm": bool(int(arm))})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    # Clip handlers
    def handle_clip_create(self, address, track, scene, length):
        try:
            self.ableton.create_midi_clip(int(track), int(scene), float(length))
            self._send_reply(address, {"status": "clip created", "track": int(track), "scene": int(scene)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    def handle_clip_add_note(self, address, track, scene, pitch, start, dur, vel):
        try:
            note = [(int(pitch), float(start), float(dur), int(vel))]
            self.ableton.add_midi_notes(int(track), int(scene), note)
            self._send_reply(address, {"status": "note added", "track": int(track), "scene": int(scene)})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})

    # Hardware controller handlers
    
    def handle_detect_controllers(self, address):
        """Auto-detect connected hardware controllers."""
        detected = self.controller_manager.auto_detect_controllers()
        self._send_reply(address, {"detected": detected})
        
    def handle_list_controllers(self, address):
        """List all connected controllers."""
        controllers = self.controller_manager.list_controllers()
        self._send_reply(address, {"controllers": controllers})
        
    def handle_connect_controller(self, address, controller_type, midi_in, midi_out):
        """
        Connect to a hardware controller.
        
        Args:
            controller_type: "push2", "push3", "launchpad_pro", etc.
            midi_in: MIDI input port name
            midi_out: MIDI output port name
        """
        try:
            if "push" in controller_type.lower():
                version = 3 if "3" in controller_type else 2
                controller = PushController(midi_in, midi_out, version)
            elif "launchpad" in controller_type.lower():
                model = "pro" if "pro" in controller_type.lower() else "x"
                controller = LaunchpadController(midi_in, midi_out, model)
            elif "apc64" in controller_type.lower():
                controller = APCController(midi_in, midi_out, "apc64")
            elif "apc_mini_mk2" in controller_type.lower() or "apc mini mk2" in controller_type.lower():
                controller = APCController(midi_in, midi_out, "apc_mini_mk2")
            else:
                self._send_reply(address, {"error": f"Unknown controller type: {controller_type}"})
                return
                
            self.controller_manager.add_controller(controller_type, controller)
            self._send_reply(address, {"status": "connected", "type": controller_type})
            
        except Exception as e:
            self._send_reply(address, {"error": str(e)})
            
    def handle_disconnect_controller(self, address, name):
        """Disconnect a controller."""
        self.controller_manager.remove_controller(name)
        self._send_reply(address, {"status": "disconnected", "name": name})
        
    def handle_set_mode(self, address, mode):
        """
        Set controller mode (chord/section/scale).
        
        Args:
            mode: "chord", "section", or "scale"
        """
        self.hardware_bridge.set_mode(mode)
        self._send_reply(address, {"status": "mode set", "mode": mode})
        
    def handle_display_progression(self, address, *args):
        """
        Display chord progression on controller.
        
        Expects: /hardware/display_progression <chords_json>
        """
        try:
            if args:
                chords_data = json.loads(args[0]) if isinstance(args[0], str) else args[0]
                # Convert JSON to Chord objects
                from arranger.models.chord import Chord
                chords = [Chord(**c) if isinstance(c, dict) else c for c in chords_data]
                self.hardware_bridge.display_chord_progression(chords)
                self._send_reply(address, {"status": "progression displayed", "count": len(chords)})
            else:
                self._send_reply(address, {"error": "No chord data provided"})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})
            
    def handle_display_arrangement(self, address, *args):
        """
        Display arrangement on controller.
        
        Expects: /hardware/display_arrangement <arrangement_json>
        """
        try:
            if args:
                arrangement_data = json.loads(args[0]) if isinstance(args[0], str) else args[0]
                from arranger.models.arrangement import Arrangement
                arrangement = Arrangement(**arrangement_data) if isinstance(arrangement_data, dict) else arrangement_data
                self.hardware_bridge.display_arrangement(arrangement)
                self._send_reply(address, {"status": "arrangement displayed"})
            else:
                self._send_reply(address, {"error": "No arrangement data provided"})
        except Exception as e:
            self._send_reply(address, {"error": str(e)})
            
    def handle_highlight_chord(self, address, chord_index):
        """Highlight a chord in the current progression."""
        self.hardware_bridge.highlight_playing_chord(int(chord_index))
        self._send_reply(address, {"status": "chord highlighted", "index": chord_index})
        
    def handle_highlight_section(self, address, section_index):
        """Highlight a section in the current arrangement."""
        self.hardware_bridge.highlight_playing_section(int(section_index))
        self._send_reply(address, {"status": "section highlighted", "index": section_index})

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
if __name__ == "__main__":
    import os
    import argparse

    parser = argparse.ArgumentParser(description="Arranger OSC server")
    parser.add_argument("--ip", default=os.getenv("ARRANGER_OSC_IP", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.getenv("ARRANGER_OSC_PORT", "12000")))
    parser.add_argument("--reply", type=int, default=int(os.getenv("ARRANGER_OSC_REPLY", "12001")))
    parser.add_argument("--live-host", default=os.getenv("ABLETON_OSC_HOST", "127.0.0.1"))
    parser.add_argument("--live-port", type=int, default=int(os.getenv("ABLETON_OSC_PORT", "11000")))
    parser.add_argument("--use-live", action="store_true", help="Connect to Ableton Live via AbletonOSC")
    args = parser.parse_args()

    server = ArrangerOSCServer(
        ip=args.ip,
        port=args.port,
        reply_port=args.reply,
        ableton_host=args.live_host,
        ableton_port=args.live_port,
        use_live=args.use_live,
    )
    server.serve_forever()
