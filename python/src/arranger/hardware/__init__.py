"""Hardware controller integration for Arranger System."""

from .controller_manager import (
    ControllerType,
    HardwareController,
    PushController,
    LaunchpadController,
    APCController,
    ControllerManager,
    get_controller_manager
)

from .hardware_bridge import (
    ArrangerHardwareBridge,
    ChordPadMode,
    SectionPadMode,
    ScalePadMode,
    get_hardware_bridge
)

__all__ = [
    # Controller types
    'ControllerType',
    'HardwareController',
    'PushController',
    'LaunchpadController',
    'APCController',
    'ControllerManager',
    'get_controller_manager',
    
    # Hardware bridge
    'ArrangerHardwareBridge',
    'ChordPadMode',
    'SectionPadMode',
    'ScalePadMode',
    'get_hardware_bridge'
]
