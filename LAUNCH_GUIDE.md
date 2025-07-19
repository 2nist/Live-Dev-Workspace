# 🚀 Devible Launch Package

**Easy Executable Launch Solutions for Devible - Professional Max for Live IDE**

Multiple deployment options for different environments and user preferences.

---

## 🎯 Quick Start Options

### **🖱️ One-Click Launch (Recommended)**

**For Windows Users:**
1. **Run Setup First**: Double-click `SETUP_DEVIBLE.bat`
   - Checks all requirements automatically
   - Guides you through any missing installations
   - Provides next-step recommendations

2. **Launch Devible**: Double-click `LAUNCH_DEVIBLE.bat`
   - Starts development server
   - Opens browser automatically
   - Installs dependencies on first run

**For macOS/Linux Users:**
1. **Make executable**: `chmod +x launch-devible.sh`
2. **Run launcher**: `./launch-devible.sh`

### **🐳 Docker Launch (Professional)**

**One-Click Docker**: Double-click `LAUNCH_DEVIBLE_DOCKER.bat`
- Containerized environment
- Includes all services and dependencies
- Production-ready configuration
- Automatic browser opening

---

## 📁 Launch Package Contents

### **📋 Setup & Diagnostics**
- `SETUP_DEVIBLE.bat` - Requirements checker and setup wizard
- `SYSTEM_CHECK.bat` - Quick system diagnostics
- `REQUIREMENTS.md` - Detailed system requirements

### **🚀 Direct Launch Scripts**
- `LAUNCH_DEVIBLE.bat` - Windows batch launcher
- `launch-devible.sh` - macOS/Linux bash launcher  
- `Launch-Devible.ps1` - PowerShell launcher (advanced)

### **🐳 Docker Deployment**
- `LAUNCH_DEVIBLE_DOCKER.bat` - One-click Docker launch
- `docker-compose.devible.yml` - Simplified Docker configuration
- `max-live-ide/Dockerfile` - Optimized container image
- `max-live-ide/nginx.conf` - Production web server config

### **📚 Documentation**
- `LAUNCH_GUIDE.md` - This comprehensive guide
- `TROUBLESHOOTING.md` - Common issues and solutions
- `DEPLOYMENT_OPTIONS.md` - Advanced deployment scenarios

---

## 🛠️ System Requirements

### **Minimum Requirements**
- **OS**: Windows 10/11, macOS 10.15+, Ubuntu 18.04+
- **RAM**: 4GB minimum, 8GB recommended
- **Storage**: 2GB free space for dependencies
- **Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

### **Development Requirements**
- **Node.js**: 18.0+ (LTS recommended)
- **npm**: 8.0+ (included with Node.js)
- **Git**: Latest version (for updates and version control)

### **Docker Requirements (Optional)**
- **Docker Desktop**: Latest version
- **RAM**: 8GB minimum for Docker deployment
- **Storage**: 5GB free space for images and volumes

### **Live Integration (Optional)**
- **Ableton Live**: 11.0+ (12.0+ recommended)
- **Max for Live**: Included with Live Suite or available separately
- **Network**: UDP port 8000 for real-time communication

---

## 🎯 Launch Options Explained

### **1. Direct Development Launch**
**Files**: `LAUNCH_DEVIBLE.bat`, `launch-devible.sh`

**Best For**:
- Development and customization
- Real-time code editing with hot reload
- Direct access to source files
- Minimal resource usage

**Process**:
1. Checks Node.js installation
2. Installs/updates dependencies
3. Starts React development server
4. Opens browser to `http://localhost:3000`

### **2. Docker Containerized Launch**
**Files**: `LAUNCH_DEVIBLE_DOCKER.bat`, `docker-compose.devible.yml`

**Best For**:
- Production-like environment
- Isolated deployment without system dependencies
- Easy sharing and distribution
- Professional testing scenarios

**Process**:
1. Builds optimized Docker images
2. Starts containerized services
3. Provides web interface on `http://localhost:3000`
4. Includes Redis caching and MinIO storage

### **3. PowerShell Launch**
**Files**: `Launch-Devible.ps1`

**Best For**:
- Windows power users
- Advanced error handling
- Corporate environments with PowerShell policies
- Detailed status reporting

---

## 🔧 Configuration Options

### **Environment Variables**
```bash
# Development Configuration
NODE_ENV=development
REACT_APP_VERSION=2.0-beta
REACT_APP_LIVE_API_URL=ws://localhost:8000
CHOKIDAR_USEPOLLING=true  # For Docker hot reload

# Production Configuration  
NODE_ENV=production
REACT_APP_API_BASE_URL=http://localhost:3000
NGINX_WORKER_PROCESSES=auto
```

### **Port Configuration**
- **Web Interface**: `3000` (customizable)
- **Live Integration**: `8000` (WebSocket)
- **Redis Cache**: `6379` (Docker only)
- **File Storage**: `9000-9001` (Docker only)

### **Development vs Production**
```javascript
// Development Features (Direct Launch)
- Hot module replacement
- Source maps enabled
- Detailed error messages
- File watching and auto-reload

// Production Features (Docker Launch)
- Optimized bundle size
- Gzip compression
- Security headers
- Health check endpoints
```

---

## 🚀 Quick Deployment Scenarios

### **Scenario 1: First-Time User**
1. Run `SETUP_DEVIBLE.bat`
2. Follow installation prompts
3. Use `LAUNCH_DEVIBLE.bat` for quick start
4. Connect to Ableton Live if available

### **Scenario 2: Beta Tester**
1. Use `LAUNCH_DEVIBLE_DOCKER.bat` for consistent environment
2. Test all features in isolated container
3. Submit feedback using built-in tools
4. Easy reset with container restart

### **Scenario 3: Developer/Contributor**
1. Use `launch-devible.sh` (macOS/Linux) or `LAUNCH_DEVIBLE.bat` (Windows)
2. Enable hot reload for development
3. Make changes and see immediate results
4. Use Git integration for version control

### **Scenario 4: Professional/Educator**
1. Docker deployment for stability
2. Multiple instances on different ports
3. Easy backup and restore with Docker volumes
4. Network deployment options

---

## 🔍 Troubleshooting Guide

### **Common Issues**

**"Node.js not found"**
```bash
Solution:
1. Download Node.js from https://nodejs.org
2. Install LTS version (18.x or higher)
3. Restart terminal/command prompt
4. Run setup script again
```

**"Docker not running"**
```bash
Solution:
1. Start Docker Desktop
2. Wait for "Docker Desktop is running" status
3. Verify with: docker --version
4. Re-run Docker launcher
```

**"Port 3000 already in use"**
```bash
Solution:
1. Kill existing processes: npx kill-port 3000
2. Or use different port: PORT=3001 npm start
3. Check for other Devible instances
```

**"Dependencies install failed"**
```bash
Solution:
1. Clear npm cache: npm cache clean --force
2. Delete node_modules folder
3. Run npm install again
4. Check network connectivity
```

### **Performance Optimization**

**Slow startup times:**
- Use Docker for faster subsequent launches
- Enable npm caching with `.npmrc` configuration
- Consider SSD storage for node_modules

**High memory usage:**
- Close unused browser tabs
- Restart Node.js process periodically
- Use Docker memory limits for constraint environments

---

## 📊 Monitoring & Logs

### **Development Logs**
```bash
# Direct launch logs
Console output shows:
- Compilation status
- Hot reload events
- Error messages
- Performance warnings

# Access logs via browser:
F12 → Console tab
```

### **Docker Logs**
```bash
# View all container logs
docker-compose -f docker-compose.devible.yml logs

# Follow specific service
docker-compose -f docker-compose.devible.yml logs -f devible

# View last 100 lines
docker-compose -f docker-compose.devible.yml logs --tail=100
```

### **Health Checks**
```bash
# Web interface health
curl http://localhost:3000/health

# Docker container status
docker-compose -f docker-compose.devible.yml ps

# System resource usage
docker stats devible-app
```

---

## 🔄 Updates & Maintenance

### **Updating Devible**
```bash
# Pull latest changes (if using Git)
git pull origin main

# Update dependencies
npm update

# Rebuild Docker images
docker-compose -f docker-compose.devible.yml build --no-cache
```

### **Backup & Restore**
```bash
# Backup Docker volumes
docker run --rm -v devible_patches:/data -v $(pwd):/backup alpine tar czf /backup/patches-backup.tar.gz -C /data .

# Restore from backup
docker run --rm -v devible_patches:/data -v $(pwd):/backup alpine tar xzf /backup/patches-backup.tar.gz -C /data
```

---

## 🎵 Ready to Create!

**Choose your preferred launch method and start creating amazing Max for Live devices:**

1. **🚀 Quick Start**: `LAUNCH_DEVIBLE.bat` for immediate development
2. **🐳 Professional**: `LAUNCH_DEVIBLE_DOCKER.bat` for production environment
3. **🔧 Setup**: `SETUP_DEVIBLE.bat` to check requirements first

**Devible: Where Ideas Become Instruments** 🎛️✨

---

*Need help? Check `TROUBLESHOOTING.md` or visit our Discord community at discord.gg/devible*
