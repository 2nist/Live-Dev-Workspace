"""Integration tests for OSC server and Live bridge."""

import pytest
import time
import threading
import json
from pythonosc import udp_client
from arranger.live_bridge.osc_server import ArrangerOSCServer


class TestOSCIntegration:
    """Test OSC server integration with backend API and Live bridge."""
    
    @pytest.fixture(scope="class")
    def osc_server(self):
        """Create and start OSC server in background thread (shared across all tests)."""
        server = ArrangerOSCServer(ip="127.0.0.1", port=12000, reply_port=12001)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        time.sleep(0.2)  # Give server time to start
        yield server
        server.server.shutdown()
        time.sleep(0.1)
    
    @pytest.fixture
    def osc_client(self):
        """Create OSC client for sending test messages."""
        return udp_client.SimpleUDPClient("127.0.0.1", 12000)
    
    def test_theory_guidance_handler(self, osc_server, osc_client, capsys):
        """Test /theory/guidance handler returns guidance."""
        osc_client.send_message("/theory/guidance", ["C", "major", "I"])
        time.sleep(0.1)  # Wait for message processing
        
        captured = capsys.readouterr()
        assert "OSC reply to /theory/guidance/reply" in captured.out
        assert "progressions" in captured.out.lower() or "cadences" in captured.out.lower()
    
    def test_progressions_handler(self, osc_server, osc_client, capsys):
        """Test /theory/progressions handler returns progressions."""
        osc_client.send_message("/theory/progressions", ["C", "major"])
        time.sleep(0.1)
        
        captured = capsys.readouterr()
        assert "OSC reply to /theory/progressions/reply" in captured.out
    
    def test_cadences_handler(self, osc_server, osc_client, capsys):
        """Test /theory/cadences handler returns cadence types."""
        osc_client.send_message("/theory/cadences", [])
        time.sleep(0.1)
        
        captured = capsys.readouterr()
        assert "OSC reply to /theory/cadences/reply" in captured.out
    
    def test_create_scene_handler(self, osc_server, osc_client, capsys):
        """Test /live/create_scene calls SceneManager."""
        osc_client.send_message("/live/create_scene", ["Verse1", "clip1", "clip2"])
        time.sleep(0.1)
        
        # Check that the scene was created in the SceneManager
        assert len(osc_server.scene_manager.scenes) == 1
        assert osc_server.scene_manager.scenes[0]["name"] == "Verse1"
        assert len(osc_server.scene_manager.scenes[0]["clips"]) == 2
        
        captured = capsys.readouterr()
        assert "scene created" in captured.out
    
    def test_create_chord_clip_handler(self, osc_server, osc_client, capsys):
        """Test /live/create_chord_clip calls ChordClipFactory."""
        osc_client.send_message("/live/create_chord_clip", ["Cmaj7", 4, 1])
        time.sleep(0.1)
        
        captured = capsys.readouterr()
        assert "clip created" in captured.out
    
    def test_schedule_playback_handler(self, osc_server, osc_client, capsys):
        """Test /live/schedule_playback calls PlaybackScheduler."""
        osc_client.send_message("/live/schedule_playback", ["V1", "C", "V2", "C", "B", "C"])
        time.sleep(0.1)
        
        # Check that the order was scheduled
        assert len(osc_server.playback_scheduler.scheduled_order) == 6
        assert osc_server.playback_scheduler.scheduled_order[0] == "V1"
        
        captured = capsys.readouterr()
        assert "playback scheduled" in captured.out
    
    def test_live_theory_suggestions_handler(self, osc_server, osc_client, capsys):
        """Test /live/theory_suggestions returns suggestions."""
        # Send JSON string instead of dict (OSC doesn't support dicts)
        live_state = json.dumps({"key": "C", "mode": "major"})
        osc_client.send_message("/live/theory_suggestions", [live_state])
        time.sleep(0.1)
        
        captured = capsys.readouterr()
        assert "OSC reply to /live/theory_suggestions/reply" in captured.out
    
    def test_analyze_arrangement_handler(self, osc_server, osc_client, capsys):
        """Test /theory/analyze_arrangement analyzes arrangement."""
        arrangement_data = {
            "key": "C",
            "mode": "major",
            "sections": [
                {"label": "V", "type": "verse", "bars": 8}
            ]
        }
        # Send JSON string instead of dict (OSC doesn't support dicts)
        osc_client.send_message("/theory/analyze_arrangement", [json.dumps(arrangement_data)])
        time.sleep(0.1)
        
        captured = capsys.readouterr()
        assert "OSC reply to /theory/analyze_arrangement/reply" in captured.out


class TestLiveBridgeIntegration:
    """Test Live bridge components integration."""
    
    def test_scene_manager_create_and_list(self):
        """Test SceneManager creates scenes and lists them."""
        from arranger.live_bridge.live_bridge import SceneManager
        
        sm = SceneManager()
        idx = sm.create_scene("Intro", [{"track": 1, "clip": "drums"}])
        assert idx == 0
        
        sm.create_scene("Verse", [{"track": 1, "clip": "bass"}])
        scenes = sm.list_scenes()
        assert len(scenes) == 2
        assert "Intro" in scenes
        assert "Verse" in scenes
    
    def test_chord_clip_factory_creates_clip(self):
        """Test ChordClipFactory generates MIDI notes."""
        from arranger.live_bridge.live_bridge import ChordClipFactory
        
        ccf = ChordClipFactory()
        result = ccf.create_chord_clip("Dm7", 4, 2)
        
        assert result["track"] == 2
        assert result["length"] == 4
        assert len(result["notes"]) > 0
        # Dm7 = D, F, A, C (notes should be present, specific octave may vary)
        # Just check we got 4 notes for a 7th chord
        assert len(result["notes"]) == 4
    
    def test_playback_scheduler_schedules_order(self):
        """Test PlaybackScheduler maintains playback order."""
        from arranger.live_bridge.live_bridge import PlaybackScheduler
        
        ps = PlaybackScheduler()
        order = ["Intro", "Verse", "Chorus", "Verse", "Bridge", "Chorus"]
        result = ps.schedule_playback(order)
        
        assert result["status"] == "scheduled"
        assert ps.get_current_order() == order
