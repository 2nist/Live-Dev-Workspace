# ALSE - Ableton Live Software Environment

A comprehensive development workspace for Ableton Live integration featuring visual Max for Live development, automated testing, and real-time synchronization.

## 🎯 What's Included

- **Python Integration**: Unified Python API combining pylive and AbletonOSC
- **Ableton-JS**: TypeScript API for Live communication
- **Max Live IDE**: React-based visual patching environment  
- **LATE**: Live Automated Testing Environment
- **Complete Documentation**: PDFs, guides, and API references

## ⚡ Quick Start

1. **Install Python Integration**
   ```bash
   cd python
   pip install -e .
   # Or use the install script: ./install.sh (macOS/Linux) or install.bat (Windows)
   ```

2. **Install JavaScript Dependencies**
   ```bash
   cd ableton-js && npm install
   cd ../max-live-ide && npm install
   ```

3. **Run Quick Test**
   ```bash
   cd python/examples
   python 01_basic_connection.py
   ```

4. **Launch IDE**
   ```bash
   cd max-live-ide
   npm start
   ```

## 📖 Documentation

- **[Python Integration Guide](python/README.md)**: Python API for M4L development
- **[Python Examples](python/examples/)**: Comprehensive example scripts
- **[Development Guide](DEVELOPMENT_GUIDE.md)**: Complete setup and usage
- **[Test Plans](ableton-live-testing/docs/test_plans.md)**: Testing strategy
- **[API Documentation](ableton-js/src/)**: JSDoc inline documentation

## 🧪 Testing Results

Latest test run: ✅ 4/5 tests passing (80% success rate)
- Mock server: ✅ Working
- Patch validation: ✅ Working  
- API endpoints: ✅ Working
- IDE responsiveness: ⏸️ (Not running)

## 🚀 Features

### Core Features
- **Python Control**: Comprehensive Python API for Live and M4L device development
- **Visual Max Patching**: Drag-and-drop Max for Live IDE
- **Real-time Synchronization**: Bidirectional Live communication
- **MIDI Generation**: Programmatic clip and note creation
- **Device Control**: Query and modify device parameters
- **Automated Testing**: Complete testing framework
- **Template Library**: Ready-to-use device templates
- **Import/Export**: .maxpat and .amxd file support

### 🎛️ **NEW: Hardware Controller Integration**

- **Akai APC64**: 64 RGB pads, 8 encoders, 8 faders - full support
- **Akai APC mini mk2**: 64 RGB pads, 8 faders, compact design - full support
- **Ableton Push 2/3 Support**: Full RGB pad control with display integration
- **Launchpad Integration**: Pro, X, and Mini models supported
- **Visual Feedback**: Chord progressions and arrangements displayed on hardware
- **Multiple Display Modes**: Chord, Section, and Scale visualization
- **Auto-Sync**: Hardware follows your composition in real-time
- **AI-Powered Composition**: Generate and visualize chords on hardware pads

📖 **[Hardware Controller Guide](DOCS/HARDWARE_CONTROLLER_GUIDE.md)** | **[APC Quick Start](DOCS/APC_QUICK_START.md)** | **[Quick Reference](DOCS/HARDWARE_QUICK_REFERENCE.md)**

## 🛠️ Requirements

- Node.js 18+
- Python 3.8+
- Ableton Live (optional for full features)
- VS Code (recommended)

---

Ready to start developing? See the [Development Guide](DEVELOPMENT_GUIDE.md) for complete instructions! 🎵
