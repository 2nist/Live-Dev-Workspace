/**
 * Contextual Tooltip System
 * Provides helpful hints and guidance throughout the interface
 */

import React, { useState, useRef, useEffect } from 'react';
import { 
  Tooltip, 
  Paper, 
  Text, 
  Group, 
  Badge,
  ActionIcon,
  ThemeIcon,
  Stack
} from '@mantine/core';
import { 
  IconHelp, 
  IconLightbulb, 
  IconInfoCircle,
  IconKeyboard,
  IconX
} from '@tabler/icons-react';
import './ContextualTooltips.css';

// Tooltip content database
const TOOLTIP_CONTENT = {
  // Toolbar tooltips
  'toolbar-new': {
    title: 'New Patch (Ctrl+N)',
    content: 'Create a blank patch to start building your device',
    shortcut: 'Ctrl+N',
    type: 'action'
  },
  'toolbar-open': {
    title: 'Open Patch (Ctrl+O)',
    content: 'Load an existing .maxpat or .amxd file',
    shortcut: 'Ctrl+O',
    type: 'action'
  },
  'toolbar-save': {
    title: 'Save Patch (Ctrl+S)',
    content: 'Save your current patch to disk',
    shortcut: 'Ctrl+S',
    type: 'action'
  },
  'toolbar-export': {
    title: 'Export to Live',
    content: 'Create a Max for Live device (.amxd) file for use in Ableton Live',
    tip: 'Save your patch first before exporting',
    type: 'action'
  },
  'toolbar-play': {
    title: 'Play (Space)',
    content: 'Start playback in Ableton Live',
    shortcut: 'Space',
    type: 'transport'
  },
  'toolbar-record': {
    title: 'Record (R)',
    content: 'Start recording in Ableton Live',
    shortcut: 'R',
    type: 'transport'
  },
  'toolbar-search': {
    title: 'Search Patch (Ctrl+F)',
    content: 'Search for objects, connections, or parameters in your patch',
    shortcut: 'Ctrl+F',
    type: 'navigation'
  },
  'toolbar-library': {
    title: 'Template Library (Ctrl+L)',
    content: 'Browse objects and templates to add to your patch',
    tip: 'Try the Quick Start templates for instant patches',
    shortcut: 'Ctrl+L',
    type: 'panel'
  },
  'toolbar-inspector': {
    title: 'Property Inspector (Ctrl+I)',
    content: 'View and edit properties of selected objects',
    tip: 'Changes update in real-time as you edit',
    shortcut: 'Ctrl+I',
    type: 'panel'
  },

  // Panel tooltips
  'panel-library': {
    title: 'Template Library',
    content: 'Drag objects and templates onto the canvas to build your patch. Use categories to browse or search to find specific items.',
    tip: 'Try the Quick Start templates for instant patches!',
    type: 'panel'
  },
  'panel-inspector': {
    title: 'Property Inspector',
    content: 'Click on any object to see its properties here. Edit parameters, view status, and access help documentation.',
    tip: 'Changes update in real-time as you edit!',
    type: 'panel'
  },
  'panel-device-manager': {
    title: 'Device Manager',
    content: 'Overview of all objects in your patch. Filter, sort, and perform bulk actions on multiple objects at once.',
    tip: 'Use filters to quickly find objects by type or status!',
    type: 'panel'
  },
  'panel-live-status': {
    title: 'Live Status Panel',
    content: 'Monitor your connection to Ableton Live, see performance metrics, and control transport.',
    tip: 'Green means connected and ready to make music!',
    type: 'status'
  },

  // Canvas tooltips
  'canvas-empty': {
    title: 'Patch Canvas',
    content: 'This is your workspace! Drag objects from the Template Library to start building your device.',
    tip: 'Right-click for context menu options!',
    type: 'workspace'
  },
  'canvas-node': {
    title: 'Max Object',
    content: 'Click to select and view properties. Drag to move. Connect ports to other objects.',
    tip: 'Double-click to edit inline parameters!',
    type: 'object'
  },
  'canvas-connection': {
    title: 'Connection',
    content: 'This carries signals between objects. Click to select, Delete key to remove.',
    tip: 'Different line styles indicate signal types (audio/control/MIDI)!',
    type: 'connection'
  }
};

// Enhanced tooltip component
const EnhancedTooltip = ({ 
  children, 
  contentId, 
  content, 
  position = 'top',
  delay = 500,
  disabled = false,
  ...props 
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [isPinned, setIsPinned] = useState(false);
  const timeoutRef = useRef();

  const tooltipData = contentId ? TOOLTIP_CONTENT[contentId] : content;

  if (!tooltipData || disabled) {
    return children;
  }

  const handleMouseEnter = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    timeoutRef.current = setTimeout(() => {
      setIsOpen(true);
    }, delay);
  };

  const handleMouseLeave = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    if (!isPinned) {
      setIsOpen(false);
    }
  };

  const handleClick = () => {
    setIsPinned(!isPinned);
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsPinned(false);
    setIsOpen(false);
  };

  const TooltipContent = () => (
    <Paper 
      p="md" 
      maw={300}
      className="enhanced-tooltip-content"
      style={{
        background: 'linear-gradient(135deg, rgba(35, 34, 126, 0.98), rgba(35, 34, 126, 0.95))',
        border: '1px solid rgba(23, 226, 195, 0.3)',
        backdropFilter: 'blur(10px)'
      }}
    >
      <Stack gap="xs">
        {/* Header */}
        <Group justify="space-between" align="flex-start">
          <Group gap="xs">
            <ThemeIcon 
              size="sm" 
              color={getTypeColor(tooltipData.type)}
              variant="light"
            >
              {getTypeIcon(tooltipData.type)}
            </ThemeIcon>
            <Text fw={600} size="sm">
              {tooltipData.title}
            </Text>
          </Group>
          {isPinned && (
            <ActionIcon 
              size="xs" 
              variant="subtle"
              onClick={handleClose}
            >
              <IconX size={12} />
            </ActionIcon>
          )}
        </Group>

        {/* Content */}
        <Text size="xs" c="dimmed" lh={1.4}>
          {tooltipData.content}
        </Text>

        {/* Tip */}
        {tooltipData.tip && (
          <Group gap="xs">
            <IconLightbulb size={12} color="#ffa500" />
            <Text size="xs" c="#ffa500" fs="italic">
              {tooltipData.tip}
            </Text>
          </Group>
        )}

        {/* Shortcut */}
        {tooltipData.shortcut && (
          <Group gap="xs">
            <IconKeyboard size={12} />
            <Badge 
              size="xs" 
              variant="light"
              color="gray"
            >
              {tooltipData.shortcut}
            </Badge>
          </Group>
        )}

        {/* Pin hint */}
        {!isPinned && (
          <Text size="xs" c="dimmed" ta="center" mt="xs">
            Click to pin this tooltip
          </Text>
        )}
      </Stack>
    </Paper>
  );

  return (
    <Tooltip
      label={<TooltipContent />}
      opened={isOpen}
      position={position}
      withArrow
      arrowSize={8}
      offset={10}
      {...props}
    >
      <div
        onMouseEnter={handleMouseEnter}
        onMouseLeave={handleMouseLeave}
        onClick={handleClick}
        style={{ display: 'inline-block' }}
      >
        {children}
      </div>
    </Tooltip>
  );
};

// Helper functions
const getTypeColor = (type) => {
  switch (type) {
    case 'action': return '#17e2c3';
    case 'transport': return '#ffa500';
    case 'navigation': return '#23227e';
    case 'panel': return '#17e2c3';
    case 'status': return '#ffa500';
    case 'workspace': return '#23227e';
    case 'object': return '#17e2c3';
    case 'connection': return '#ffa500';
    default: return 'gray';
  }
};

const getTypeIcon = (type) => {
  switch (type) {
    case 'action': return <IconInfoCircle size={12} />;
    case 'transport': return <IconInfoCircle size={12} />;
    case 'navigation': return <IconHelp size={12} />;
    case 'panel': return <IconInfoCircle size={12} />;
    case 'status': return <IconInfoCircle size={12} />;
    case 'workspace': return <IconHelp size={12} />;
    case 'object': return <IconInfoCircle size={12} />;
    case 'connection': return <IconInfoCircle size={12} />;
    default: return <IconHelp size={12} />;
  }
};

// Help button component for panels
const HelpButton = ({ contentId, size = 'sm' }) => {
  return (
    <EnhancedTooltip contentId={contentId} position="bottom-start">
      <ActionIcon 
        variant="subtle" 
        size={size}
        c="dimmed"
        className="help-button"
      >
        <IconHelp size={14} />
      </ActionIcon>
    </EnhancedTooltip>
  );
};

// Global tooltip provider
const TooltipProvider = ({ children, disabled = false }) => {
  useEffect(() => {
    // Add global tooltip data attributes for dynamic tooltips
    const addTooltipAttributes = () => {
      // Toolbar elements
      const toolbarButtons = document.querySelectorAll('[data-tooltip]');
      toolbarButtons.forEach(button => {
        const tooltipId = button.getAttribute('data-tooltip');
        if (TOOLTIP_CONTENT[tooltipId]) {
          button.setAttribute('title', TOOLTIP_CONTENT[tooltipId].title);
        }
      });
    };

    addTooltipAttributes();
    
    // Re-run when DOM changes
    const observer = new MutationObserver(addTooltipAttributes);
    observer.observe(document.body, { 
      childList: true, 
      subtree: true 
    });

    return () => observer.disconnect();
  }, []);

  return (
    <div className={`tooltip-provider ${disabled ? 'tooltips-disabled' : ''}`}>
      {children}
    </div>
  );
};

export { 
  EnhancedTooltip, 
  HelpButton, 
  TooltipProvider,
  TOOLTIP_CONTENT 
};
