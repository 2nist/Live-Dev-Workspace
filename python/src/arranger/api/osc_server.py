"""
OSC Server stub for theory guidance endpoints.

Routes OSC messages to music theory API functions for progressions, cadences, substitutions, and more.
"""

from arranger.api import theory

# Example OSC handler registration (pseudo-code)
def handle_osc_message(address, *args):
    if address == "/theory/progressions":
        key, mode = args
        return theory.api_get_progressions(key, mode)
    elif address == "/theory/cadences":
        return theory.api_get_cadences()
    elif address == "/theory/add_progression":
        mode, progression = args[0], args[1:]
        return theory.api_add_progression(mode, list(progression))
    elif address == "/theory/add_cadence":
        name, chords = args[0], args[1:]
        return theory.api_add_cadence(name, list(chords))
    elif address == "/theory/guidance":
        # args: key, mode, chord
        context = {"key": args[0], "mode": args[1], "chord": args[2]}
        return theory.api_get_theory_guidance(context)
    # ...other endpoints
    return {"error": "Unknown address"}

# To integrate, connect this handler to your OSC server's message dispatch system.
# Example: osc_server.add_handler("/theory/progressions", handle_osc_message)
