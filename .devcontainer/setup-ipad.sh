#!/bin/bash

# iPad Development Environment Setup Script
echo "🎹📱 Setting up Max Live IDE for iPad Development..."

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Create development directories
echo -e "${BLUE}📁 Creating development directories...${NC}"
mkdir -p /workspaces/ALSE/max-live-ide/src/mobile
mkdir -p /workspaces/ALSE/max-live-ide/src/components/mobile
mkdir -p /workspaces/ALSE/max-live-ide/src/hooks/mobile
mkdir -p /workspaces/ALSE/max-live-ide/src/styles/mobile
mkdir -p /workspaces/ALSE/max-live-ide/docs/mobile

# Install iPad-specific development dependencies
echo -e "${BLUE}📦 Installing iPad development dependencies...${NC}"
cd /workspaces/ALSE/max-live-ide

# Check if package.json exists, create if not
if [ ! -f package.json ]; then
    echo -e "${YELLOW}⚠️  Creating package.json...${NC}"
    npm init -y
fi

# Install mobile/touch development packages
npm install --save-dev @types/hammerjs hammerjs
npm install --save react-spring framer-motion
npm install --save-dev @testing-library/react @testing-library/jest-dom
npm install --save-dev cypress @cypress/react

# Install responsive design utilities
npm install --save @mantine/core @mantine/hooks @mantine/notifications
npm install --save react-use-gesture
npm install --save react-responsive

echo -e "${GREEN}✅ Dependencies installed successfully!${NC}"

# Set up mobile testing configuration
echo -e "${BLUE}🧪 Setting up mobile testing configuration...${NC}"

# Create Cypress config for mobile testing
cat > cypress.config.js << 'EOF'
const { defineConfig } = require('cypress');

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1024,
    viewportHeight: 768,
    video: false,
    screenshot: true,
    screenshotOnRunFailure: true,
  },
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack',
    },
    viewportWidth: 768,
    viewportHeight: 1024,
  },
});
EOF

# Create mobile viewport test configurations
mkdir -p cypress/support
cat > cypress/support/mobile-commands.js << 'EOF'
// Custom commands for mobile testing
Cypress.Commands.add('setMobileViewport', (device = 'ipad') => {
  const viewports = {
    'ipad': [768, 1024],
    'ipad-pro': [834, 1194],
    'iphone': [375, 812]
  };
  
  const [width, height] = viewports[device];
  cy.viewport(width, height);
});

Cypress.Commands.add('testTouch', (selector) => {
  cy.get(selector).trigger('touchstart');
  cy.get(selector).trigger('touchend');
});
EOF

# Create development launch script
cat > start-ipad-dev.sh << 'EOF'
#!/bin/bash
echo "🎹📱 Starting Max Live IDE for iPad Development..."

# Set iPad development environment variables
export IPAD_DEV=true
export MOBILE_DEBUG=true
export TOUCH_INTERFACE=enabled
export REACT_APP_MOBILE_MODE=true

# Start development server with mobile optimizations
npm start
EOF

chmod +x start-ipad-dev.sh

echo -e "${GREEN}✅ Mobile testing configuration created!${NC}"

# Create iPad development documentation
echo -e "${BLUE}📚 Creating iPad development documentation...${NC}"

cat > docs/mobile/IPAD_DEVELOPMENT_GUIDE.md << 'EOF'
# iPad Development Guide

## Overview
This guide covers developing the Max Live IDE for iPad using GitHub Codespaces.

## Setup
1. Open the repository in GitHub Codespaces
2. The environment will automatically configure for iPad development
3. Use the `start-ipad-dev.sh` script to launch with mobile optimizations

## Mobile-Specific Features
- Touch-optimized interface
- Responsive design breakpoints
- Gesture support with Hammer.js
- Mobile debugging tools
- Viewport testing configurations

## Testing on iPad
1. Use the forwarded port to access the app on your iPad
2. Enable mobile debugging in Safari
3. Test touch interactions and gestures
4. Use Cypress for automated mobile testing

## Key Considerations
- Touch target sizes (minimum 44px)
- Gesture conflicts with iOS
- Safari-specific behavior
- Performance on mobile hardware
- Network connectivity issues

## Development Workflow
1. Make changes in Codespaces
2. Test on forwarded port
3. Use Safari Dev Tools for debugging
4. Commit changes to ipad-development branch
EOF

echo -e "${GREEN}✅ Documentation created!${NC}"

# Final setup steps
echo -e "${BLUE}🔧 Final setup steps...${NC}"

# Install global tools if needed
npm list -g @storybook/cli || npm install -g @storybook/cli

echo -e "${GREEN}🎉 iPad Development Environment Setup Complete!${NC}"
echo -e "${YELLOW}📋 Next Steps:${NC}"
echo "1. Run './start-ipad-dev.sh' to start development server"
echo "2. Open the forwarded port on your iPad"
echo "3. Begin developing mobile-optimized features"
echo "4. Use 'npm run test:mobile' for mobile-specific tests"

# Create package.json scripts for mobile development
echo -e "${BLUE}📦 Adding mobile development scripts...${NC}"

# Add mobile-specific scripts to package.json
node -e "
const pkg = require('./package.json');
pkg.scripts = pkg.scripts || {};
pkg.scripts['start:mobile'] = './start-ipad-dev.sh';
pkg.scripts['test:mobile'] = 'cypress open --config viewportWidth=768,viewportHeight=1024';
pkg.scripts['test:mobile:ci'] = 'cypress run --config viewportWidth=768,viewportHeight=1024';
pkg.scripts['build:mobile'] = 'REACT_APP_MOBILE_MODE=true npm run build';
require('fs').writeFileSync('./package.json', JSON.stringify(pkg, null, 2));
"

echo -e "${GREEN}✅ All setup complete! 🎹📱${NC}"
EOF
