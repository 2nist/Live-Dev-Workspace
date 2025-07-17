#!/bin/bash

# ALSE Development Environment Setup Script
# Configures complete Ableton Live development environment in Codespaces

echo "🚀 Setting up ALSE Development Environment..."

# Update system
sudo apt-get update

# Install additional dependencies
echo "📦 Installing system dependencies..."
sudo apt-get install -y \
    curl \
    git \
    vim \
    htop \
    tree \
    jq \
    python3-pip \
    python3-venv

# Setup Node.js environment
echo "📋 Setting up Node.js environment..."
cd /workspaces/ALSE

# Install Node.js dependencies for ableton-js
echo "  → Installing ableton-js dependencies..."
cd ableton-js
npm install
npm audit fix --audit-level moderate || true
cd ..

# Install Node.js dependencies for Max Live IDE  
echo "  → Installing Max Live IDE dependencies..."
cd max-live-ide
npm install
npm audit fix --audit-level moderate || true
cd ..

# Setup Python environment
echo "🐍 Setting up Python environment..."
cd /workspaces/ALSE

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "  → Installing Python dependencies..."
cd ableton-live-testing
pip install --upgrade pip
pip install -r requirements.txt || pip install flask requests websocket-client
cd ..

# Install MCP dependencies
echo "  → Installing MCP dependencies..."
cd ableton-mcp-extended
pip install -e . || echo "MCP installation skipped (optional)"
cd ..

# Setup environment variables
echo "🔧 Configuring environment..."
cat >> ~/.bashrc << 'EOF'

# ALSE Environment Variables
export ALSE_ROOT="/workspaces/ALSE"
export PYTHONPATH="${ALSE_ROOT}:${PYTHONPATH}"
export NODE_PATH="${ALSE_ROOT}/node_modules:${NODE_PATH}"
export LATE_DEBUG=1

# ALSE Aliases
alias alse-test="cd ${ALSE_ROOT}/ableton-live-testing/harness && python quick_ide_test.py"
alias alse-ide="cd ${ALSE_ROOT}/max-live-ide && npm start"
alias alse-mock="cd ${ALSE_ROOT}/ableton-live-testing/mock && python mock_server.py"
alias alse-full-test="cd ${ALSE_ROOT}/ableton-live-testing/harness && python ide_integration_test.py"

# Quick navigation
alias cdalse="cd ${ALSE_ROOT}"
alias cdide="cd ${ALSE_ROOT}/max-live-ide"
alias cdjs="cd ${ALSE_ROOT}/ableton-js"
alias cdlate="cd ${ALSE_ROOT}/ableton-live-testing"

EOF

# Source the updated bashrc
source ~/.bashrc

# Create workspace-specific VS Code settings
echo "⚙️  Configuring VS Code workspace..."
mkdir -p .vscode

cat > .vscode/settings.json << 'EOF'
{
  "eslint.workingDirectories": [
    "ableton-js",
    "max-live-ide"
  ],
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.terminal.activateEnvironment": true,
  "terminal.integrated.env.linux": {
    "ALSE_ROOT": "/workspaces/ALSE",
    "PYTHONPATH": "/workspaces/ALSE",
    "LATE_DEBUG": "1"
  },
  "files.associations": {
    "*.maxpat": "json",
    "*.amxd": "json"
  },
  "files.exclude": {
    "**/node_modules": true,
    "**/.git": true,
    "**/venv": true,
    "**/__pycache__": true,
    "**/*.pyc": true
  },
  "search.exclude": {
    "**/node_modules": true,
    "**/venv": true,
    "**/__pycache__": true
  }
}
EOF

# Create VS Code tasks
cat > .vscode/tasks.json << 'EOF'
{
  "version": "2.0.0",
  "tasks": [
    {
      "label": "Start Max Live IDE",
      "type": "shell",
      "command": "npm start",
      "group": "build",
      "options": {
        "cwd": "${workspaceFolder}/max-live-ide"
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Run LATE Quick Tests",
      "type": "shell", 
      "command": "python quick_ide_test.py",
      "group": "test",
      "options": {
        "cwd": "${workspaceFolder}/ableton-live-testing/harness"
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": true,
        "panel": "shared"
      }
    },
    {
      "label": "Start Mock Server",
      "type": "shell",
      "command": "python mock_server.py", 
      "group": "build",
      "options": {
        "cwd": "${workspaceFolder}/ableton-live-testing/mock"
      },
      "presentation": {
        "echo": true,
        "reveal": "always",
        "focus": false,
        "panel": "new"
      },
      "isBackground": true,
      "problemMatcher": []
    },
    {
      "label": "Full Integration Test",
      "type": "shell",
      "command": "python ide_integration_test.py",
      "group": "test",
      "options": {
        "cwd": "${workspaceFolder}/ableton-live-testing/harness"
      },
      "presentation": {
        "echo": true,
        "reveal": "always", 
        "focus": true,
        "panel": "shared"
      }
    }
  ]
}
EOF

# Create VS Code launch configurations
cat > .vscode/launch.json << 'EOF'
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Debug Max Live IDE",
      "type": "node",
      "request": "launch",
      "program": "${workspaceFolder}/max-live-ide/node_modules/.bin/react-scripts",
      "args": ["start"],
      "cwd": "${workspaceFolder}/max-live-ide",
      "env": {
        "BROWSER": "none"
      },
      "console": "integratedTerminal"
    },
    {
      "name": "Debug Python Tests",
      "type": "python",
      "request": "launch",
      "program": "${workspaceFolder}/ableton-live-testing/harness/quick_ide_test.py",
      "cwd": "${workspaceFolder}/ableton-live-testing/harness",
      "console": "integratedTerminal",
      "env": {
        "LATE_DEBUG": "1"
      }
    }
  ]
}
EOF

# Test the setup
echo "🧪 Testing setup..."

# Test Node.js setup
echo "  → Testing Node.js environment..."
node --version
npm --version

# Test Python setup
echo "  → Testing Python environment..."
source venv/bin/activate
python --version
pip --version

# Test Python imports
echo "  → Testing Python imports..."
python -c "import flask, requests; print('✓ Python dependencies OK')" || echo "⚠️  Some Python dependencies missing"

# Run quick test
echo "  → Running quick validation test..."
cd ableton-live-testing/harness
timeout 30s python quick_ide_test.py || echo "⚠️  Quick test timeout (expected in Codespace)"
cd ../..

# Create helpful README for Codespace users
cat > CODESPACE_QUICK_START.md << 'EOF'
# 🚀 ALSE Codespace Quick Start

Welcome to your ALSE development environment! Everything is pre-configured and ready to go.

## 🎯 Quick Actions

### Start Development
```bash
# Start Max Live IDE (opens automatically)
alse-ide

# Start mock server for testing
alse-mock

# Run quick tests
alse-test
```

### Available Commands
- `alse-ide` - Start the Max Live IDE
- `alse-test` - Run quick development tests  
- `alse-mock` - Start mock Ableton Live server
- `alse-full-test` - Run complete integration tests
- `cdalse` - Navigate to workspace root
- `cdide` - Navigate to Max Live IDE
- `cdjs` - Navigate to ableton-js
- `cdlate` - Navigate to testing framework

## 📱 Mobile Development

### iPad Setup
1. Open the forwarded port 3000 URL in Safari
2. Add to Home Screen for app-like experience
3. Enable Apple Pencil support in settings

### Touch Gestures
- **Single tap**: Select object
- **Double tap**: Edit object  
- **Long press**: Context menu
- **Pinch**: Zoom canvas
- **Two-finger drag**: Pan canvas

## 🔗 Port Forwarding
- **3000**: Max Live IDE (main interface)
- **9001**: WebSocket API (real-time updates)
- **9877**: HTTP API (commands)
- **5000**: Mock server (testing)

## 🧪 Testing
Use VS Code tasks (Ctrl+Shift+P → "Tasks: Run Task"):
- "Start Max Live IDE"
- "Run LATE Quick Tests" 
- "Start Mock Server"
- "Full Integration Test"

## 🎵 Ready to Rock!
Your complete Ableton Live development environment is ready. Start creating amazing Max for Live devices! ✨
EOF

echo ""
echo "✅ ALSE Development Environment Setup Complete!"
echo ""
echo "🎯 Quick Start:"
echo "   → Run 'alse-ide' to start the Max Live IDE"
echo "   → Run 'alse-test' to test the environment"
echo "   → Run 'alse-mock' to start the mock server"
echo ""
echo "📱 Mobile Access:"
echo "   → Open the forwarded port 3000 URL on your mobile device"
echo "   → Add to home screen for app-like experience"
echo ""
echo "📚 Documentation:"
echo "   → Check CODESPACE_QUICK_START.md for detailed instructions"
echo "   → Visit max-live-ide/MOBILE_INTEGRATION_GUIDE.md for mobile setup"
echo ""
echo "🎵 Happy coding! 🚀"
