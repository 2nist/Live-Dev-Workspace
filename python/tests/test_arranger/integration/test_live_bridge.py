import os
import time
import unittest

# Ensure python/src is on the path when running directly
WORKSPACE_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
PY_SRC = os.path.join(WORKSPACE_ROOT, "src")
if PY_SRC not in os.sys.path:
    os.sys.path.insert(0, PY_SRC)

from arranger.live_bridge.ableton_connection import AbletonConnection
from arranger.live_bridge.live_bridge import SceneManager, ChordClipFactory, PlaybackScheduler
from arranger.models.chord import Chord


class TestLiveBridgeMock(unittest.TestCase):
    def setUp(self):
        # Use mock mode explicitly
        self.conn = AbletonConnection(mock=True, auto_reconnect=False)
        # If connection failed, AbletonConnection should fall back to mock
        self.scene_mgr = SceneManager(self.conn)
        self.clip_factory = ChordClipFactory()
        self.scheduler = PlaybackScheduler(self.conn)

    def test_transport_and_scenes(self):
        # Transport
        self.conn.set_tempo(124.5)
        self.assertAlmostEqual(self.conn.get_tempo(), 124.5, places=1)
        self.conn.play()
        self.assertTrue(self.conn.is_playing())
        self.conn.stop()
        self.assertFalse(self.conn.is_playing())

        # Scenes
        initial = self.conn.get_num_scenes()
        idx = self.conn.create_scene(index=-1)
        self.conn.set_scene_name(idx, "Intro")
        self.assertEqual(self.conn.get_num_scenes(), initial + 1)
        names = self.conn.get_scene_names()
        self.assertIn("Intro", names)
        self.conn.set_scene_name(idx, "Intro A")
        names2 = self.conn.get_scene_names()
        self.assertIn("Intro A", names2)

    def test_clip_creation_and_schedule(self):
        # Prepare a chord progression
        chords = [Chord.from_name("Cmaj7"), Chord.from_name("Am7"), Chord.from_name("Dm7"), Chord.from_name("G7")]
        # Create scene and clip
        scene_idx = self.conn.create_scene(index=-1)
        track_idx = 0
        clip_name = "Prog1-Clip"
        # In mock mode, index returns None; use 0 for subsequent calls (no-ops in mock)
        self.conn.create_midi_clip(track_idx, scene_idx, length=4.0)
        clip_idx = 0
        self.conn.set_clip_name(track_idx, clip_idx, clip_name)
        # Add notes for first chord
        pitches = chords[0].to_midi_notes(octave=4)
        notes = [(p, 0.0, 1.0, 96) for p in pitches]
        self.conn.add_midi_notes(track_idx, clip_idx, notes)

        # Schedule playback order and trigger next (mock validation)
        self.conn.set_scene_name(scene_idx, "Prog 1")
        result = self.scheduler.schedule_playback(["Prog 1"])  # mock mode returns scheduled order
        self.assertEqual(result.get("order"), ["Prog 1"]) 
        next_label = self.scheduler.trigger_next()
        self.assertEqual(next_label, "Prog 1")


if __name__ == "__main__":
    unittest.main()
