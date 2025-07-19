/**
 * Object & Template Browser Demo
 * Demonstrates all features of the browser system
 */

import React, { useState } from 'react';
import { 
  Paper, 
  Button, 
  Group, 
  Stack, 
  Text, 
  Code,
  Badge,
  Alert,
  List,
  Title,
  Divider
} from '@mantine/core';
import { 
  IconBook, 
  IconZap, 
  IconTemplate, 
  IconHeart,
  IconTarget,
  IconKeyboard,
  IconInfoCircle
} from '@tabler/icons-react';
import ObjectTemplateBrowser from './ObjectTemplateBrowser';

const ObjectBrowserDemo = () => {
  const [demoOpen, setDemoOpen] = useState(false);
  const [lastSelected, setLastSelected] = useState(null);

  const handleObjectSelect = (object) => {
    setLastSelected({ type: 'object', item: object });
    console.log('Demo: Selected object:', object);
  };

  const handleTemplateSelect = (template) => {
    setLastSelected({ type: 'template', item: template });
    console.log('Demo: Selected template:', template);
  };

  return (
    <Paper p="lg" shadow="sm" radius="md">
      <Stack gap="lg">
        {/* Header */}
        <Group gap="sm">
          <IconBook size={24} color="#007acc" />
          <Title order={2}>Object & Template Browser Demo</Title>
          <Badge variant="light" color="blue">Interactive Demo</Badge>
        </Group>

        {/* Description */}
        <Alert icon={<IconInfoCircle size={16} />} title="What's Included" color="blue">
          <Text size="sm">
            A comprehensive search and browsing system for Max objects, Live API objects, 
            Live devices, and pre-built templates. Perfect for quickly finding and adding 
            components to your Max Live IDE patches.
          </Text>
        </Alert>

        {/* Features List */}
        <div>
          <Text fw={600} mb="sm">🌟 Key Features:</Text>
          <List size="sm" spacing="xs">
            <List.Item icon={<IconZap size={16} color="#17e2c3" />}>
              <strong>25+ Max Objects</strong> - Audio generators, MIDI processors, utility objects
            </List.Item>
            <List.Item icon={<IconTemplate size={16} color="#4a9c3a" />}>
              <strong>Live API Objects</strong> - live.dial, live.gain~, live.object, and more
            </List.Item>
            <List.Item icon={<IconBook size={16} color="#ffa500" />}>
              <strong>Live Devices Database</strong> - Wavetable, Operator, Reverb, EQ Eight
            </List.Item>
            <List.Item icon={<IconTarget size={16} color="#007acc" />}>
              <strong>Quick Templates</strong> - Pre-built patches for instant workflow
            </List.Item>
            <List.Item icon={<IconHeart size={16} color="#e74c3c" />}>
              <strong>Smart Features</strong> - Favorites, recent items, advanced filtering
            </List.Item>
          </List>
        </div>

        {/* Database Preview */}
        <div>
          <Text fw={600} mb="sm">📚 Object Database Preview:</Text>
          <Group gap="md">
            <Paper p="sm" withBorder>
              <Group gap="xs">
                <IconZap size={14} color="#17e2c3" />
                <Text size="xs" fw={500}>Audio Objects</Text>
              </Group>
              <Text size="xs" c="dimmed" mt="xs">
                osc~, cycle~, saw~, biquad~, gain~, delay~, noise~, ezdac~
              </Text>
            </Paper>
            <Paper p="sm" withBorder>
              <Group gap="xs">
                <IconZap size={14} color="#ffa500" />
                <Text size="xs" fw={500}>MIDI Objects</Text>
              </Group>
              <Text size="xs" c="dimmed" mt="xs">
                notein, noteout, ctlin, ctlout, makenote, stripnote
              </Text>
            </Paper>
            <Paper p="sm" withBorder>
              <Group gap="xs">
                <IconZap size={14} color="#4a9c3a" />
                <Text size="xs" fw={500}>Live API</Text>
              </Group>
              <Text size="xs" c="dimmed" mt="xs">
                live.dial, live.gain~, live.object, live.observer
              </Text>
            </Paper>
          </Group>
        </div>

        {/* Keyboard Shortcuts */}
        <div>
          <Text fw={600} mb="sm">⌨️ Keyboard Shortcuts:</Text>
          <Group gap="md">
            <Group gap="xs">
              <Code>Ctrl+Shift+O</Code>
              <Text size="sm">Open Browser</Text>
            </Group>
            <Group gap="xs">
              <Code>Ctrl+F</Code>
              <Text size="sm">Focus Search</Text>
            </Group>
            <Group gap="xs">
              <Code>Esc</Code>
              <Text size="sm">Close Browser</Text>
            </Group>
            <Group gap="xs">
              <Code>↑↓</Code>
              <Text size="sm">Navigate</Text>
            </Group>
            <Group gap="xs">
              <Code>Enter</Code>
              <Text size="sm">Select</Text>
            </Group>
          </Group>
        </div>

        {/* Last Selected */}
        {lastSelected && (
          <Alert color="green" title="✅ Selection Made!">
            <Text size="sm">
              {lastSelected.type === 'object' ? 'Object' : 'Template'}: <strong>{lastSelected.item.name}</strong>
            </Text>
            <Text size="xs" c="dimmed" mt="xs">
              {lastSelected.item.description}
            </Text>
          </Alert>
        )}

        <Divider />

        {/* Demo Controls */}
        <Group justify="center" gap="md">
          <Button
            leftSection={<IconBook size={16} />}
            onClick={() => setDemoOpen(true)}
            size="lg"
            gradient={{ from: 'blue', to: 'cyan' }}
          >
            Open Object Browser Demo
          </Button>
          {lastSelected && (
            <Button
              variant="light"
              onClick={() => setLastSelected(null)}
              size="lg"
            >
              Clear Selection
            </Button>
          )}
        </Group>

        {/* Usage Instructions */}
        <Paper p="md" bg="gray.0" radius="md">
          <Text fw={600} mb="sm">💡 How to Use:</Text>
          <List size="sm" spacing="xs">
            <List.Item>Click "Open Object Browser Demo" to explore the interface</List.Item>
            <List.Item>Try searching for objects like "osc", "gain", "live.dial"</List.Item>
            <List.Item>Filter by category (Audio, MIDI, Live API) or tags</List.Item>
            <List.Item>Preview objects with the eye icon to see details</List.Item>
            <List.Item>Add items to favorites with the heart icon</List.Item>
            <List.Item>Select objects or templates to see them added to your patch</List.Item>
          </List>
        </Paper>
      </Stack>

      {/* Demo Browser */}
      <ObjectTemplateBrowser
        isVisible={demoOpen}
        onObjectSelect={handleObjectSelect}
        onTemplateSelect={handleTemplateSelect}
        onClose={() => setDemoOpen(false)}
      />
    </Paper>
  );
};

export default ObjectBrowserDemo;
