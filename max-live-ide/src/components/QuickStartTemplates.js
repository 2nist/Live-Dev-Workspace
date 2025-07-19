/**
 * Quick Start Templates
 * Pre-built patches for instant device creation
 */

import React from 'react';
import { 
  Paper, 
  Text, 
  Group, 
  Stack, 
  Badge,
  Button,
  SimpleGrid,
  ThemeIcon,
  ActionIcon
} from '@mantine/core';
import { 
  IconMusic, 
  IconWaveSquare, 
  IconDevices,
  IconBolt,
  IconStar,
  IconDownload,
  IconEye
} from '@tabler/icons-react';
import './QuickStartTemplates.css';

const QUICK_START_TEMPLATES = [
  {
    id: 'simple-synth',
    name: 'Simple Synth',
    description: 'Basic oscillator with filter and envelope',
    category: 'Instrument',
    difficulty: 'Beginner',
    icon: IconMusic,
    color: '#17e2c3',
    objects: ['live.dial', 'osc~', 'live.gain~', 'ezdac~'],
    connections: 3,
    preview: '/previews/simple-synth.png',
    tags: ['synth', 'oscillator', 'basic'],
    patch: {
      nodes: [
        {
          id: 'freq-dial',
          type: 'maxObject',
          position: { x: 100, y: 100 },
          data: { 
            label: 'live.dial @parameter_enable 1',
            objectType: 'live',
            status: 'connected',
            tags: ['control', 'parameter']
          }
        },
        {
          id: 'osc',
          type: 'maxObject', 
          position: { x: 100, y: 200 },
          data: {
            label: 'osc~ 440',
            objectType: 'audio',
            status: 'connected',
            tags: ['oscillator', 'audio', 'generator']
          }
        },
        {
          id: 'gain',
          type: 'maxObject',
          position: { x: 100, y: 300 },
          data: {
            label: 'live.gain~ @parameter_enable 1',
            objectType: 'live',
            status: 'connected', 
            tags: ['volume', 'control']
          }
        },
        {
          id: 'output',
          type: 'maxObject',
          position: { x: 100, y: 400 },
          data: {
            label: 'ezdac~',
            objectType: 'audio',
            status: 'connected',
            tags: ['output', 'dac']
          }
        }
      ],
      edges: [
        {
          id: 'freq-to-osc',
          source: 'freq-dial',
          target: 'osc',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        },
        {
          id: 'osc-to-gain',
          source: 'osc', 
          target: 'gain',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        },
        {
          id: 'gain-to-output',
          source: 'gain',
          target: 'output', 
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        }
      ]
    }
  },
  {
    id: 'midi-effect',
    name: 'MIDI Effect',
    description: 'Note processor with velocity and timing control',
    category: 'MIDI Effect',
    difficulty: 'Beginner',
    icon: IconBolt,
    color: '#ffa500',
    objects: ['notein', 'velocity', 'noteout'],
    connections: 2,
    tags: ['midi', 'effect', 'notes'],
    patch: {
      nodes: [
        {
          id: 'midi-in',
          type: 'maxObject',
          position: { x: 100, y: 100 },
          data: {
            label: 'notein',
            objectType: 'midi',
            status: 'connected',
            tags: ['input', 'midi', 'notes']
          }
        },
        {
          id: 'velocity-scale',
          type: 'maxObject',
          position: { x: 250, y: 200 },
          data: {
            label: 'live.dial @parameter_enable 1',
            objectType: 'live',
            status: 'connected',
            tags: ['control', 'velocity']
          }
        },
        {
          id: 'midi-out',
          type: 'maxObject',
          position: { x: 100, y: 300 },
          data: {
            label: 'noteout',
            objectType: 'midi',
            status: 'connected',
            tags: ['output', 'midi', 'notes']
          }
        }
      ],
      edges: [
        {
          id: 'in-to-out',
          source: 'midi-in',
          target: 'midi-out',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        },
        {
          id: 'velocity-to-out',
          source: 'velocity-scale',
          target: 'midi-out',
          sourceHandle: 'outlet-0', 
          targetHandle: 'inlet-1'
        }
      ]
    }
  },
  {
    id: 'audio-effect',
    name: 'Audio Effect',
    description: 'Signal processing chain with filter and delay',
    category: 'Audio Effect',
    difficulty: 'Intermediate', 
    icon: IconWaveSquare,
    color: '#23227e',
    objects: ['live.in~', 'biquad~', 'live.out~'],
    connections: 4,
    tags: ['audio', 'effect', 'filter'],
    patch: {
      nodes: [
        {
          id: 'audio-in',
          type: 'maxObject',
          position: { x: 100, y: 100 },
          data: {
            label: 'live.in~',
            objectType: 'live',
            status: 'connected',
            tags: ['input', 'audio']
          }
        },
        {
          id: 'filter',
          type: 'maxObject',
          position: { x: 100, y: 200 },
          data: {
            label: 'biquad~ @parameter_enable 1',
            objectType: 'audio',
            status: 'connected',
            tags: ['filter', 'effect', 'audio']
          }
        },
        {
          id: 'audio-out',
          type: 'maxObject',
          position: { x: 100, y: 300 },
          data: {
            label: 'live.out~',
            objectType: 'live',
            status: 'connected',
            tags: ['output', 'audio']
          }
        }
      ],
      edges: [
        {
          id: 'in-to-filter',
          source: 'audio-in',
          target: 'filter',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        },
        {
          id: 'filter-to-out',
          source: 'filter',
          target: 'audio-out',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        }
      ]
    }
  },
  {
    id: 'live-api',
    name: 'Live API Control',
    description: 'Control Ableton Live parameters and transport',
    category: 'Live Integration',
    difficulty: 'Advanced',
    icon: IconDevices,
    color: '#17e2c3',
    objects: ['live.object', 'live.observer', 'live.button'],
    connections: 2,
    tags: ['live', 'api', 'control'],
    patch: {
      nodes: [
        {
          id: 'live-object',
          type: 'maxObject',
          position: { x: 100, y: 100 },
          data: {
            label: 'live.object live_set',
            objectType: 'live',
            status: 'connected',
            tags: ['api', 'live', 'control']
          }
        },
        {
          id: 'play-button',
          type: 'maxObject',
          position: { x: 250, y: 200 },
          data: {
            label: 'live.button @parameter_enable 1',
            objectType: 'live',
            status: 'connected',
            tags: ['button', 'transport', 'control']
          }
        }
      ],
      edges: [
        {
          id: 'button-to-object',
          source: 'play-button',
          target: 'live-object',
          sourceHandle: 'outlet-0',
          targetHandle: 'inlet-0'
        }
      ]
    }
  }
];

const getDifficultyColor = (difficulty) => {
  switch (difficulty) {
    case 'Beginner': return 'green';
    case 'Intermediate': return 'orange';
    case 'Advanced': return 'red';
    default: return 'gray';
  }
};

const QuickStartTemplate = ({ 
  template, 
  onSelect, 
  onPreview,
  isSelected = false 
}) => {
  const Icon = template.icon;
  
  return (
    <Paper
      p="md"
      radius="md"
      className={`quick-start-template ${isSelected ? 'selected' : ''}`}
      style={{
        cursor: 'pointer',
        transition: 'all 0.2s ease',
        border: `2px solid ${isSelected ? template.color : 'transparent'}`,
        background: `linear-gradient(135deg, 
          rgba(35, 34, 126, 0.1) 0%, 
          rgba(35, 34, 126, 0.05) 100%)`
      }}
      onClick={() => onSelect(template)}
    >
      <Stack gap="sm">
        {/* Header */}
        <Group justify="space-between" align="flex-start">
          <Group gap="sm">
            <ThemeIcon
              size="lg"
              color={template.color}
              variant="light"
              radius="md"
            >
              <Icon size={20} />
            </ThemeIcon>
            <div>
              <Text fw={600} size="sm">
                {template.name}
              </Text>
              <Text size="xs" c="dimmed">
                {template.category}
              </Text>
            </div>
          </Group>
          
          <Group gap="xs">
            <Badge 
              size="xs" 
              color={getDifficultyColor(template.difficulty)}
              variant="light"
            >
              {template.difficulty}
            </Badge>
            {onPreview && (
              <ActionIcon
                size="sm"
                variant="subtle"
                onClick={(e) => {
                  e.stopPropagation();
                  onPreview(template);
                }}
              >
                <IconEye size={14} />
              </ActionIcon>
            )}
          </Group>
        </Group>

        {/* Description */}
        <Text size="xs" c="dimmed" lh={1.4}>
          {template.description}
        </Text>

        {/* Stats */}
        <Group justify="space-between" align="center">
          <Group gap="md">
            <Group gap="xs">
              <Text size="xs" c="dimmed">Objects:</Text>
              <Text size="xs" fw={500}>
                {template.objects?.length || 0}
              </Text>
            </Group>
            <Group gap="xs">
              <Text size="xs" c="dimmed">Connections:</Text>
              <Text size="xs" fw={500}>
                {template.connections || 0}
              </Text>
            </Group>
          </Group>
          
          <IconDownload 
            size={14} 
            color={template.color}
            style={{ opacity: 0.7 }}
          />
        </Group>

        {/* Tags */}
        {template.tags && (
          <Group gap="xs">
            {template.tags.slice(0, 3).map(tag => (
              <Badge 
                key={tag}
                size="xs"
                variant="dot"
                color="gray"
              >
                {tag}
              </Badge>
            ))}
            {template.tags.length > 3 && (
              <Text size="xs" c="dimmed">
                +{template.tags.length - 3} more
              </Text>
            )}
          </Group>
        )}
      </Stack>
    </Paper>
  );
};

const QuickStartTemplates = ({ 
  onTemplateSelect,
  onTemplatePreview,
  selectedTemplate = null,
  gridColumns = 2
}) => {
  return (
    <Stack gap="md">
      {/* Header */}
      <Group justify="space-between" align="center">
        <Group gap="xs">
          <IconStar size={16} color="#ffa500" />
          <Text fw={600} size="sm">
            Quick Start Templates
          </Text>
        </Group>
        <Badge variant="light" size="xs">
          Get started instantly
        </Badge>
      </Group>

      {/* Templates Grid */}
      <SimpleGrid cols={gridColumns} spacing="md">
        {QUICK_START_TEMPLATES.map(template => (
          <QuickStartTemplate
            key={template.id}
            template={template}
            onSelect={onTemplateSelect}
            onPreview={onTemplatePreview}
            isSelected={selectedTemplate?.id === template.id}
          />
        ))}
      </SimpleGrid>

      {/* Help Text */}
      <Text size="xs" c="dimmed" ta="center" fs="italic">
        Click any template to add it to your canvas
      </Text>
    </Stack>
  );
};

export { 
  QuickStartTemplates, 
  QuickStartTemplate,
  QUICK_START_TEMPLATES 
};
