/**
 * Onboarding Tour Component
 * Interactive step-by-step guided tour for first-time users
 */

import React, { useState, useEffect, useCallback } from 'react';
import { 
  Modal, 
  Paper, 
  Title, 
  Text, 
  Button, 
  Group, 
  Stack, 
  Progress,
  Badge,
  Spotlight,
  Overlay,
  ActionIcon,
  ThemeIcon
} from '@mantine/core';
import { 
  IconX, 
  IconChevronLeft, 
  IconChevronRight,
  IconCheck,
  IconMusic,
  IconWand,
  IconRocket
} from '@tabler/icons-react';
import './OnboardingTour.css';

const TOUR_STEPS = [
  {
    id: 'welcome',
    title: 'Welcome to Devible! 🎵',
    content: `Ready to create amazing Max for Live devices? Devible makes visual patching intuitive and powerful.

This quick tour will show you everything you need to know to start building your first device in under 5 minutes.

✨ **What you'll learn:**
• How to browse and add objects
• Building your first patch  
• Connecting to Ableton Live
• Exporting your device

Let's get started!`,
    highlight: null,
    interactive: false,
    icon: IconMusic,
    color: '#17e2c3'
  },
  {
    id: 'canvas',
    title: 'Your Creative Canvas',
    content: `This is where the magic happens! The patch canvas is your workspace for building Max for Live devices.

🎛️ **Canvas Features:**
• Drag objects around to organize your patch
• Connect objects by dragging between their ports
• Zoom and pan to navigate large patches
• Right-click for context menus

**Pro Tip:** Use Ctrl+Mouse Wheel to zoom, or click the fit button in the toolbar!`,
    highlight: '.react-flow',
    interactive: false,
    icon: IconWand,
    color: '#23227e'
  },
  {
    id: 'library',
    title: 'Your Object Palette',
    content: `The Template Library is your toolbox! Browse through categories of Max objects and pre-built templates.

📚 **How to use:**
• Browse categories (Audio Effects, Instruments, MIDI, etc.)
• Drag objects directly onto the canvas
• Use the search box to find specific objects
• Try the Quick Start templates for instant results

Let's add your first object!`,
    highlight: '.template-library',
    interactive: false,
    icon: IconRocket,
    color: '#ffa500'
  },
  {
    id: 'quickstart',
    title: 'Instant Patch Creation',
    content: `Let's create your first patch! Click on the 'Simple Synth' template below.

🚀 **Quick Start Templates:**
• **Simple Synth** - Basic oscillator and filter
• **MIDI Effect** - Note processor template  
• **Audio Effect** - Signal processing chain
• **Live API Control** - Ableton integration

Go ahead, click 'Simple Synth' to see it in action!`,
    highlight: '.quick-start-templates',
    interactive: true,
    requiredAction: 'click-template',
    icon: IconRocket,
    color: '#17e2c3'
  },
  {
    id: 'connections',
    title: 'Connecting Objects',
    content: `Great! You've added a synth template. Now let's understand connections.

🔗 **Connection Types:**
• **Audio** (thick lines) - Sound signals
• **Control** (thin lines) - Parameter data  
• **MIDI** (dashed lines) - Note information

**Try it:** Drag from an output port ● to an input port ● to create a connection.

The synth template already has audio connected to the output - you can hear it in Live!`,
    highlight: '.react-flow__edge',
    interactive: false,
    icon: IconCheck,
    color: '#23227e'
  },
  {
    id: 'inspector',
    title: 'Fine-Tune Your Objects',
    content: `Click on any object to see its properties here. The Inspector lets you:

⚙️ **Inspector Powers:**
• Adjust object parameters and settings
• See real-time status and values
• Edit object names and descriptions
• Access help documentation

**Try it:** Click on the oscillator object and change its frequency!`,
    highlight: '.property-inspector',
    interactive: true,
    requiredAction: 'click-object',
    icon: IconWand,
    color: '#ffa500'
  },
  {
    id: 'live-status',
    title: 'Connect to Ableton Live',
    content: `The Live Status shows your connection to Ableton Live. When connected, you can:

🎵 **Live Integration:**
• Hear your patches in real-time
• Control Live's transport (play/stop/record)
• Access Live's devices and parameters
• Sync with Live's tempo and time

**Status:** Connected ✅ | Disconnected ❌

Your patch is ready to make sound!`,
    highlight: '.live-status-panel',
    interactive: false,
    icon: IconMusic,
    color: '#17e2c3'
  },
  {
    id: 'export',
    title: 'Share Your Creation',
    content: `Ready to use your device in Live? The Export button creates a Max for Live device (.amxd) file.

📤 **Export Process:**
• Click Export to Live in the toolbar
• Your device appears in Live's browser
• Drag it onto a track to use it
• Share your .amxd file with others

**Pro Tip:** Save your project first (Ctrl+S) before exporting!`,
    highlight: '.export-button',
    interactive: false,
    icon: IconRocket,
    color: '#23227e'
  },
  {
    id: 'complete',
    title: "You're Ready to Rock! 🎸",
    content: `Congratulations! You now know the essentials of Devible.

🎯 **What's Next:**
• **Explore** more objects in the Template Library
• **Experiment** with different Quick Start templates  
• **Connect** objects to build complex patches
• **Export** and use your devices in Live

**Need Help?** Press F1 for help, or hover over any UI element for tooltips.

Happy patching!`,
    highlight: null,
    interactive: false,
    icon: IconCheck,
    color: '#17e2c3'
  }
];

const OnboardingTour = ({ 
  isOpen, 
  onComplete, 
  onSkip,
  onStepComplete 
}) => {
  const [currentStep, setCurrentStep] = useState(0);
  const [completedActions, setCompletedActions] = useState(new Set());
  const [highlightElement, setHighlightElement] = useState(null);

  const step = TOUR_STEPS[currentStep];
  const progress = ((currentStep + 1) / TOUR_STEPS.length) * 100;

  // Highlight management
  useEffect(() => {
    if (step.highlight) {
      const element = document.querySelector(step.highlight);
      setHighlightElement(element);
      
      if (element) {
        element.scrollIntoView({ 
          behavior: 'smooth', 
          block: 'center' 
        });
      }
    } else {
      setHighlightElement(null);
    }
  }, [currentStep, step.highlight]);

  // Handle required actions
  const handleRequiredAction = useCallback((action) => {
    if (step.requiredAction === action) {
      setCompletedActions(prev => new Set(prev).add(step.id));
      onStepComplete?.(step.id, action);
    }
  }, [step, onStepComplete]);

  // Navigation
  const goToNext = () => {
    if (currentStep < TOUR_STEPS.length - 1) {
      setCurrentStep(currentStep + 1);
    } else {
      onComplete();
    }
  };

  const goToPrevious = () => {
    if (currentStep > 0) {
      setCurrentStep(currentStep - 1);
    }
  };

  const canProceed = !step.interactive || completedActions.has(step.id);

  // Spotlight effect for highlighted elements
  const SpotlightOverlay = () => {
    if (!highlightElement) return null;

    const rect = highlightElement.getBoundingClientRect();
    const spotlightStyle = {
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      background: `radial-gradient(circle at ${rect.left + rect.width/2}px ${rect.top + rect.height/2}px, transparent ${Math.max(rect.width, rect.height)/2 + 20}px, rgba(0,0,0,0.7) ${Math.max(rect.width, rect.height)/2 + 60}px)`,
      pointerEvents: 'none',
      zIndex: 1000
    };

    return <div style={spotlightStyle} />;
  };

  if (!isOpen) return null;

  return (
    <>
      <SpotlightOverlay />
      
      <Modal
        opened={isOpen}
        onClose={onSkip}
        size="lg"
        centered
        withCloseButton={false}
        overlayProps={{
          backgroundOpacity: 0,
          blur: 0
        }}
        styles={{
          modal: {
            position: 'relative',
            zIndex: 1001,
            maxWidth: '500px'
          }
        }}
      >
        <Paper p="xl" radius="md">
          {/* Header */}
          <Group justify="space-between" mb="md">
            <Group>
              <ThemeIcon 
                size="lg" 
                radius="md" 
                color={step.color}
                variant="light"
              >
                <step.icon size={20} />
              </ThemeIcon>
              <div>
                <Title order={3}>{step.title}</Title>
                <Text size="sm" c="dimmed">
                  Step {currentStep + 1} of {TOUR_STEPS.length}
                </Text>
              </div>
            </Group>
            <ActionIcon 
              variant="subtle" 
              onClick={onSkip}
              aria-label="Skip tour"
            >
              <IconX size={16} />
            </ActionIcon>
          </Group>

          {/* Progress */}
          <Progress 
            value={progress} 
            mb="lg" 
            color={step.color}
            size="sm"
            radius="md"
          />

          {/* Content */}
          <Stack gap="md" mb="xl">
            <Text 
              style={{ whiteSpace: 'pre-line' }}
              size="sm"
              lh={1.6}
            >
              {step.content}
            </Text>

            {step.interactive && !canProceed && (
              <Badge 
                color="orange" 
                variant="light"
                leftSection="👆"
              >
                Complete the action above to continue
              </Badge>
            )}

            {step.interactive && canProceed && (
              <Badge 
                color="green" 
                variant="light"
                leftSection="✅"
              >
                Great job! Ready to continue
              </Badge>
            )}
          </Stack>

          {/* Navigation */}
          <Group justify="space-between">
            <Button
              variant="subtle"
              leftSection={<IconChevronLeft size={16} />}
              onClick={goToPrevious}
              disabled={currentStep === 0}
            >
              Back
            </Button>

            <Group>
              <Button
                variant="subtle"
                onClick={onSkip}
              >
                Skip Tour
              </Button>
              
              <Button
                rightSection={
                  currentStep === TOUR_STEPS.length - 1 ? 
                    <IconCheck size={16} /> : 
                    <IconChevronRight size={16} />
                }
                onClick={goToNext}
                disabled={!canProceed}
                color={step.color}
              >
                {currentStep === TOUR_STEPS.length - 1 ? 'Start Creating!' : 'Next'}
              </Button>
            </Group>
          </Group>
        </Paper>
      </Modal>
    </>
  );
};

export default OnboardingTour;
