"""
Hardware Controller Manager for Ableton Push, Launchpad, and other surfaces.

Provides unified interface for hardware controller integration with arranger system.
"""
import logging
from typing import Dict, List, Optional, Callable
from enum import Enum

logger = logging.getLogger(__name__)


class ControllerType(Enum):
    """Supported controller types."""
    PUSH_2 = "push2"
    PUSH_3 = "push3"
    LAUNCHPAD_PRO = "launchpad_pro"
    LAUNCHPAD_MINI = "launchpad_mini"
    LAUNCHPAD_X = "launchpad_x"
    APC40 = "apc40"
    APC64 = "apc64"
    APC_MINI_MK2 = "apc_mini_mk2"
    APC_KEY_25 = "apc_key_25"
    GENERIC_MIDI = "generic_midi"


class ControllerCapabilities:
    """Defines capabilities of a hardware controller."""
    
    def __init__(self, controller_type: ControllerType):
        self.type = controller_type
        self.has_pads = True
        self.has_encoders = False
        self.has_display = False
        self.has_touchstrip = False
        self.pad_count = 64
        self.encoder_count = 0
        
        # Configure based on type
        if controller_type == ControllerType.PUSH_2:
            self.has_encoders = True
            self.has_display = True
            self.has_touchstrip = True
            self.encoder_count = 8
            self.pad_count = 64
            
        elif controller_type == ControllerType.PUSH_3:
            self.has_encoders = True
            self.has_display = True
            self.has_touchstrip = True
            self.encoder_count = 8
            self.pad_count = 64
            # Push 3 has MPE support
            self.has_mpe = True
            
        elif controller_type in [ControllerType.LAUNCHPAD_PRO, ControllerType.LAUNCHPAD_X]:
            self.pad_count = 64
            self.has_encoders = False
            
        elif controller_type == ControllerType.LAUNCHPAD_MINI:
            self.pad_count = 64
            
        elif controller_type == ControllerType.APC40:
            self.has_encoders = True
            self.has_faders = True
            self.encoder_count = 8
            self.fader_count = 9
            self.pad_count = 40
            
        elif controller_type == ControllerType.APC64:
            self.has_encoders = True
            self.has_faders = True
            self.encoder_count = 8
            self.fader_count = 8
            self.pad_count = 64
            # APC64 has RGB pads
            self.has_rgb = True
            
        elif controller_type == ControllerType.APC_MINI_MK2:
            self.has_faders = True
            self.fader_count = 8
            self.pad_count = 64
            # APC mini mk2 has RGB pads
            self.has_rgb = True


class HardwareController:
    """Base class for hardware controller integration."""
    
    def __init__(self, controller_type: ControllerType, midi_in_port: str, midi_out_port: str):
        self.type = controller_type
        self.capabilities = ControllerCapabilities(controller_type)
        self.midi_in_port = midi_in_port
        self.midi_out_port = midi_out_port
        self.connected = False
        
        # State tracking
        self.pad_states = {}  # {pad_index: color/velocity}
        self.encoder_values = {}  # {encoder_index: value}
        self.button_states = {}  # {button_name: pressed}
        
        # Callbacks
        self.pad_callbacks = []
        self.encoder_callbacks = []
        self.button_callbacks = []
        
    def connect(self):
        """Connect to hardware controller via MIDI."""
        try:
            # Import mido for MIDI communication
            import mido
            
            self.midi_in = mido.open_input(self.midi_in_port)
            self.midi_out = mido.open_output(self.midi_out_port)
            self.connected = True
            logger.info(f"Connected to {self.type.value} on {self.midi_in_port}")
            
            # Initialize controller
            self._initialize_controller()
            
        except Exception as e:
            logger.error(f"Failed to connect to controller: {e}")
            self.connected = False
            
    def disconnect(self):
        """Disconnect from hardware controller."""
        if hasattr(self, 'midi_in'):
            self.midi_in.close()
        if hasattr(self, 'midi_out'):
            self.midi_out.close()
        self.connected = False
        
    def _initialize_controller(self):
        """Initialize controller to known state (override in subclass)."""
        pass
        
    def on_pad_press(self, callback: Callable):
        """Register callback for pad press events."""
        self.pad_callbacks.append(callback)
        
    def on_encoder_change(self, callback: Callable):
        """Register callback for encoder change events."""
        self.encoder_callbacks.append(callback)
        
    def on_button_press(self, callback: Callable):
        """Register callback for button press events."""
        self.button_callbacks.append(callback)
        
    def set_pad_color(self, pad_index: int, color: tuple):
        """Set RGB color for a pad."""
        raise NotImplementedError("Subclass must implement")
        
    def set_pad_brightness(self, pad_index: int, brightness: int):
        """Set brightness for a pad (0-127)."""
        raise NotImplementedError("Subclass must implement")
        
    def clear_all_pads(self):
        """Clear all pad illumination."""
        raise NotImplementedError("Subclass must implement")


class PushController(HardwareController):
    """Ableton Push 2/3 controller integration."""
    
    def __init__(self, midi_in_port: str, midi_out_port: str, version: int = 2):
        controller_type = ControllerType.PUSH_3 if version == 3 else ControllerType.PUSH_2
        super().__init__(controller_type, midi_in_port, midi_out_port)
        self.version = version
        
    def _initialize_controller(self):
        """Initialize Push to User Mode."""
        import mido
        
        # Enter User Mode (allows custom MIDI control)
        # SysEx message for Push 2/3
        user_mode_msg = mido.Message.from_bytes([0xF0, 0x00, 0x21, 0x1D, 0x01, 0x01, 0x0A, 0x01, 0xF7])
        self.midi_out.send(user_mode_msg)
        
        # Clear all pads
        self.clear_all_pads()
        logger.info(f"Push {self.version} initialized in User Mode")
        
    def set_pad_color(self, pad_index: int, color: tuple):
        """
        Set RGB color for Push pad.
        
        Args:
            pad_index: Pad number (0-63)
            color: RGB tuple (r, g, b) where values are 0-127
        """
        import mido
        
        if not self.connected:
            return
            
        # Push uses note numbers 36-99 for pads (8x8 grid)
        note = 36 + pad_index
        
        # Send RGB color via SysEx
        # Push color format: velocity-based for simple colors
        # For RGB: use SysEx message
        r, g, b = color
        
        # Simplified: use velocity for brightness
        brightness = int((r + g + b) / 3)
        
        msg = mido.Message('note_on', note=note, velocity=brightness, channel=0)
        self.midi_out.send(msg)
        
        self.pad_states[pad_index] = color
        
    def clear_all_pads(self):
        """Turn off all pad LEDs."""
        import mido
        
        if not self.connected:
            return
            
        for pad in range(64):
            note = 36 + pad
            msg = mido.Message('note_off', note=note, channel=0)
            self.midi_out.send(msg)
            
        self.pad_states = {}
        
    def display_text(self, line: int, text: str):
        """
        Display text on Push display (if available).
        
        Args:
            line: Display line number (0-3 for Push 2, more for Push 3)
            text: Text to display
        """
        if self.version == 3:
            # Push 3 has full color display - would need display protocol
            logger.info(f"Push 3 display: Line {line}: {text}")
        else:
            # Push 2 has LCD displays above encoders
            logger.info(f"Push 2 display: Line {line}: {text}")


class APCController(HardwareController):
    """Akai APC64 and APC mini mk2 controller integration."""
    
    def __init__(self, midi_in_port: str, midi_out_port: str, model: str = "apc64"):
        controller_map = {
            "apc64": ControllerType.APC64,
            "apc_mini_mk2": ControllerType.APC_MINI_MK2
        }
        controller_type = controller_map.get(model, ControllerType.APC64)
        super().__init__(controller_type, midi_in_port, midi_out_port)
        self.model = model
        
        # APC-specific MIDI channels
        self.pad_channel = 0  # Channel 1
        self.button_channel = 0
        
    def _initialize_controller(self):
        """Initialize APC to generic mode."""
        import mido
        
        # APC controllers work in generic MIDI mode by default
        # Clear all pads
        self.clear_all_pads()
        logger.info(f"APC {self.model} initialized in generic MIDI mode")
        
    def set_pad_color(self, pad_index: int, color: tuple):
        """
        Set RGB color for APC pad.
        
        APC64: 64 RGB pads in 8x8 grid
        APC mini mk2: 64 RGB pads in 8x8 grid
        
        Args:
            pad_index: Pad number (0-63)
            color: RGB tuple (r, g, b) where values are 0-127
        """
        import mido
        
        if not self.connected:
            return
            
        # Calculate MIDI note from pad index
        # APC pads are arranged in 8x8 grid
        row = pad_index // 8
        col = pad_index % 8
        
        if self.model == "apc64":
            # APC64 pad layout: notes 0-63 (bottom to top, left to right)
            # Row 0 (bottom) = notes 0-7
            # Row 7 (top) = notes 56-63
            note = (7 - row) * 8 + col
        else:  # apc_mini_mk2
            # APC mini mk2 pad layout: notes 0-63 (top to bottom, left to right)
            # Row 0 (top) = notes 0-7
            # Row 7 (bottom) = notes 56-63
            note = row * 8 + col
        
        # Convert RGB to velocity-based color
        # APC uses velocity 1-127 for different colors
        velocity = self._rgb_to_apc_velocity(color)
        
        msg = mido.Message('note_on', note=note, velocity=velocity, channel=self.pad_channel)
        self.midi_out.send(msg)
        
        self.pad_states[pad_index] = color
        
    def _rgb_to_apc_velocity(self, color: tuple) -> int:
        """
        Convert RGB to APC velocity color.
        
        APC color palette (velocity-based):
        0 = Off
        1-5 = Red (dim to bright)
        6-11 = Orange
        12-16 = Yellow
        17-21 = Green
        22-26 = Cyan
        27-31 = Blue
        32-36 = Purple
        37+ = Various colors and brightness levels
        """
        r, g, b = color
        
        # Determine dominant color
        max_component = max(r, g, b)
        
        if max_component < 20:
            return 0  # Off
            
        # Calculate brightness (1-5 scale)
        brightness = int((max_component / 127) * 4) + 1
        
        # Red
        if r > g and r > b:
            return brightness  # Red (1-5)
        # Green
        elif g > r and g > b:
            return 17 + (brightness - 1)  # Green (17-21)
        # Blue
        elif b > r and b > g:
            return 27 + (brightness - 1)  # Blue (27-31)
        # Yellow (R+G)
        elif r > 80 and g > 80 and b < 50:
            return 12 + (brightness - 1)  # Yellow (12-16)
        # Cyan (G+B)
        elif g > 80 and b > 80 and r < 50:
            return 22 + (brightness - 1)  # Cyan (22-26)
        # Purple (R+B)
        elif r > 80 and b > 80 and g < 50:
            return 32 + (brightness - 1)  # Purple (32-36)
        # Orange (R+some G)
        elif r > 80 and 30 < g < 80:
            return 6 + (brightness - 1)  # Orange (6-11)
        # White/Gray
        elif abs(r - g) < 30 and abs(g - b) < 30:
            return 37 + brightness  # White range
        else:
            # Default to red with brightness
            return brightness
            
    def clear_all_pads(self):
        """Turn off all APC pad LEDs."""
        import mido
        
        if not self.connected:
            return
            
        # Send note off to all 64 pads
        for pad in range(64):
            row = pad // 8
            col = pad % 8
            
            if self.model == "apc64":
                note = (7 - row) * 8 + col
            else:
                note = row * 8 + col
                
            msg = mido.Message('note_off', note=note, channel=self.pad_channel)
            self.midi_out.send(msg)
            
        self.pad_states = {}
        
    def set_fader(self, fader_index: int, value: int):
        """
        Set fader position (APC64 and APC mini mk2 both have 8 faders).
        
        Args:
            fader_index: Fader number (0-7)
            value: Fader value (0-127)
        """
        import mido
        
        if not self.connected:
            return
            
        if fader_index >= 8:
            return
            
        # Faders use CC messages
        # APC64/mini mk2: CC 48-55 for faders 1-8
        cc_number = 48 + fader_index
        
        msg = mido.Message('control_change', control=cc_number, value=value, channel=self.pad_channel)
        self.midi_out.send(msg)


class LaunchpadController(HardwareController):
    """Novation Launchpad controller integration."""
    
    def __init__(self, midi_in_port: str, midi_out_port: str, model: str = "pro"):
        controller_map = {
            "pro": ControllerType.LAUNCHPAD_PRO,
            "x": ControllerType.LAUNCHPAD_X,
            "mini": ControllerType.LAUNCHPAD_MINI
        }
        controller_type = controller_map.get(model, ControllerType.LAUNCHPAD_PRO)
        super().__init__(controller_type, midi_in_port, midi_out_port)
        self.model = model
        
    def _initialize_controller(self):
        """Initialize Launchpad to Programmer Mode."""
        import mido
        
        # Enter Programmer Mode
        # SysEx for Launchpad Pro: F0 00 20 29 02 10 2C 03 F7
        sysex_msg = mido.Message.from_bytes([0xF0, 0x00, 0x20, 0x29, 0x02, 0x10, 0x2C, 0x03, 0xF7])
        self.midi_out.send(sysex_msg)
        
        # Clear all pads
        self.clear_all_pads()
        logger.info(f"Launchpad {self.model} initialized in Programmer Mode")
        
    def set_pad_color(self, pad_index: int, color: tuple):
        """Set RGB color for Launchpad pad."""
        import mido
        
        if not self.connected:
            return
            
        # Launchpad uses velocity for color palette or RGB SysEx
        # Simplified: map RGB to closest palette color
        r, g, b = color
        
        # Launchpad color palette (simplified)
        velocity = self._rgb_to_launchpad_color(r, g, b)
        
        # Grid note numbers start at 11 (not 0)
        note = self._index_to_note(pad_index)
        
        msg = mido.Message('note_on', note=note, velocity=velocity, channel=0)
        self.midi_out.send(msg)
        
        self.pad_states[pad_index] = color
        
    def _rgb_to_launchpad_color(self, r: int, g: int, b: int) -> int:
        """Map RGB to Launchpad velocity color palette."""
        # Simplified color mapping
        if r > 100 and g < 50 and b < 50:
            return 5  # Red
        elif r < 50 and g > 100 and b < 50:
            return 21  # Green
        elif r < 50 and g < 50 and b > 100:
            return 45  # Blue
        elif r > 100 and g > 100 and b < 50:
            return 13  # Yellow
        else:
            return 3  # White/dim
            
    def _index_to_note(self, pad_index: int) -> int:
        """Convert pad index to MIDI note number."""
        # Launchpad grid: 8x8 starting at note 11
        row = pad_index // 8
        col = pad_index % 8
        return (row * 10) + col + 11
        
    def clear_all_pads(self):
        """Turn off all Launchpad LEDs."""
        import mido
        
        if not self.connected:
            return
            
        # Send note off to all pads
        for row in range(8):
            for col in range(8):
                note = (row * 10) + col + 11
                msg = mido.Message('note_off', note=note, channel=0)
                self.midi_out.send(msg)
                
        self.pad_states = {}


class ControllerManager:
    """Manages multiple hardware controllers."""
    
    def __init__(self):
        self.controllers: Dict[str, HardwareController] = {}
        self.active_controller: Optional[HardwareController] = None
        
    def add_controller(self, name: str, controller: HardwareController):
        """Add a hardware controller to the manager."""
        self.controllers[name] = controller
        controller.connect()
        
        if not self.active_controller:
            self.active_controller = controller
            
        logger.info(f"Added controller: {name} ({controller.type.value})")
        
    def remove_controller(self, name: str):
        """Remove and disconnect a controller."""
        if name in self.controllers:
            self.controllers[name].disconnect()
            del self.controllers[name]
            
            if self.active_controller and self.active_controller == self.controllers.get(name):
                self.active_controller = None
                
    def set_active_controller(self, name: str):
        """Set the active controller."""
        if name in self.controllers:
            self.active_controller = self.controllers[name]
            logger.info(f"Active controller set to: {name}")
            
    def get_active_controller(self) -> Optional[HardwareController]:
        """Get the currently active controller."""
        return self.active_controller
        
    def list_controllers(self) -> List[Dict]:
        """List all connected controllers."""
        return [
            {
                "name": name,
                "type": ctrl.type.value,
                "connected": ctrl.connected,
                "capabilities": {
                    "pads": ctrl.capabilities.pad_count,
                    "encoders": ctrl.capabilities.encoder_count if ctrl.capabilities.has_encoders else 0,
                    "display": ctrl.capabilities.has_display
                }
            }
            for name, ctrl in self.controllers.items()
        ]
        
    def auto_detect_controllers(self) -> List[str]:
        """Auto-detect connected hardware controllers."""
        try:
            import mido
            
            detected = []
            ports = mido.get_input_names()
            
            # Look for known controller names
            controller_patterns = {
                "Push 2": ("push2", PushController),
                "Push 3": ("push3", PushController),
                "Launchpad Pro": ("launchpad_pro", LaunchpadController),
                "Launchpad X": ("launchpad_x", LaunchpadController),
                "Launchpad Mini": ("launchpad_mini", LaunchpadController),
                "APC64": ("apc64", "APCController"),
                "APC mini mk2": ("apc_mini_mk2", "APCController"),
            }
            
            for port in ports:
                for pattern, (name, controller_class) in controller_patterns.items():
                    if pattern.lower() in port.lower():
                        detected.append({
                            "name": name,
                            "port": port,
                            "type": pattern
                        })
                        
            return detected
            
        except Exception as e:
            logger.error(f"Failed to auto-detect controllers: {e}")
            return []


# Singleton instance
_controller_manager = None

def get_controller_manager() -> ControllerManager:
    """Get the global controller manager instance."""
    global _controller_manager
    if _controller_manager is None:
        _controller_manager = ControllerManager()
    return _controller_manager
