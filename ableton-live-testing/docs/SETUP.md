# LATE Setup Guide

This guide describes how to set up the Live Automated Testing Environment (LATE) for Ableton Live development.

## Prerequisites
- Ableton Live installed
- Python 3.x (for scripting and automation)
- Node.js (if using JS/TS tools)
- Recommended: Virtual audio/MIDI devices for automation

## Steps
1. Clone or copy the LATE folder into your workspace.
2. Configure Ableton Live for remote/script access:
   - Enable Max for Live and Python Remote Scripts.
   - Set up test sets and example projects in `/tests/`.
3. Install dependencies for harness and mock tools:
   - See `/harness/README.md` and `/mock/README.md` for details.
4. Run example tests:
   - Use provided scripts in `/harness/` for real Live automation.
   - Use `/mock/` for fast, simulated API tests.

## Tips
- Use versioned test sets for reproducibility.
- Integrate with CI/CD for continuous validation.
- Document custom scripts and test cases in `/docs/`.

---
For troubleshooting, see Ableton Live API docs in `/DOCS` and `/ableton-js/README.md`.
