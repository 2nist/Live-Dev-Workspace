# ALSE - Ableton Live Software Environment

A comprehensive development workspace for Ableton Live integration featuring visual Max for Live development, automated testing, and real-time synchronization.

## 🎯 What's Included

- **Ableton-JS**: TypeScript API for Live communication
- **Max Live IDE**: React-based visual patching environment  
- **LATE**: Live Automated Testing Environment
- **Complete Documentation**: PDFs, guides, and API references

## ⚡ Quick Start

1. **Install Dependencies**
   ```bash
   cd ableton-js && npm install
   cd ../max-live-ide && npm install
   cd ../ableton-live-testing && pip install -r requirements.txt
   ```

2. **Run Quick Test**
   ```bash
   cd ableton-live-testing/harness
   python quick_ide_test.py
   ```

3. **Launch IDE**
   ```bash
   cd max-live-ide
   npm start
   ```

## 📖 Documentation

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

- Visual drag-and-drop Max patching
- Real-time Ableton Live synchronization
- Automated testing framework
- Template library for common devices
- Import/export .maxpat and .amxd files

## 🛠️ Requirements

- Node.js 18+
- Python 3.8+
- Ableton Live (optional for full features)
- VS Code (recommended)

---

Ready to start developing? See the [Development Guide](DEVELOPMENT_GUIDE.md) for complete instructions! 🎵
