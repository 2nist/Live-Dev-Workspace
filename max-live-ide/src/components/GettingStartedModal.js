/**
 * M4L Getting Started Panel
 * Helpful tips and quick tutorials for beginners
 */

import React, { useState } from 'react';
import {
  Modal,
  Stack,
  Text,
  Button,
  Group,
  Badge,
  Paper,
  ThemeIcon,
  Stepper,
  Code,
  List,
  Divider,
  Accordion,
  ActionIcon
} from '@mantine/core';
import {
  IconRobot,
  IconBulb,
  IconCode,
  IconMusic,
  IconWand,
  IconCheck,
  IconX
} from '@tabler/icons-react';

export function GettingStartedModal({ opened, onClose, onStartTutorial }) {
  const [activeStep, setActiveStep] = useState(0);
  const [dontShowAgain, setDontShowAgain] = useState(false);

  const handleClose = () => {
    if (dontShowAgain) {
      localStorage.setItem('m4l_hide_getting_started', 'true');
    }
    onClose();
  };

  const quickTutorials = [
    {
      icon: IconMusic,
      title: 'Create Your First MIDI Effect',
      difficulty: 'Beginner',
      time: '5 min',
      description: 'Learn to transpose MIDI notes',
      prompt: 'Help me create a simple MIDI transposer'
    },
    {
      icon: IconCode,
      title: 'Write JavaScript Code',
      difficulty: 'Intermediate',
      time: '10 min',
      description: 'Build a custom MIDI processor',
      prompt: 'Show me how to write JavaScript for a scale quantizer'
    },
    {
      icon: IconWand,
      title: 'Control Live with Max',
      difficulty: 'Intermediate',
      time: '15 min',
      description: 'Use the Live API',
      prompt: 'How do I control Live parameters from Max?'
    }
  ];

  return (
    <Modal
      opened={opened}
      onClose={handleClose}
      title="Welcome to Max Live IDE!"
      size="xl"
      centered
    >
      <Stack gap="lg">
        {/* Introduction */}
        <Paper p="md" withBorder style={{ backgroundColor: 'var(--mantine-color-blue-0)' }}>
          <Group gap="md">
            <ThemeIcon size="xl" variant="light">
              <IconRobot size={28} />
            </ThemeIcon>
            <div style={{ flex: 1 }}>
              <Text fw={600} size="lg">AI-Powered M4L Development</Text>
              <Text size="sm" c="dimmed">
                Build Max for Live devices with AI assistance. No prior Max experience required!
              </Text>
            </div>
          </Group>
        </Paper>

        {/* Key Features */}
        <div>
          <Text fw={600} mb="sm">What You Can Do:</Text>
          <List
            spacing="xs"
            icon={
              <ThemeIcon color="teal" size={20} radius="xl">
                <IconCheck size={12} />
              </ThemeIcon>
            }
          >
            <List.Item>
              <Text size="sm"><strong>Ask the AI anything</strong> - Get instant help and code generation</Text>
            </List.Item>
            <List.Item>
              <Text size="sm"><strong>Build MIDI effects</strong> - Process notes, create arpeggators, and more</Text>
            </List.Item>
            <List.Item>
              <Text size="sm"><strong>Control Ableton Live</strong> - Access the Live API from Max</Text>
            </List.Item>
            <List.Item>
              <Text size="sm"><strong>Write JavaScript</strong> - Create custom logic with built-in AI assistance</Text>
            </List.Item>
          </List>
        </div>

        <Divider />

        {/* Quick Start Tutorials */}
        <div>
          <Text fw={600} mb="md">Quick Start Tutorials:</Text>
          <Stack gap="xs">
            {quickTutorials.map((tutorial, index) => (
              <Paper key={index} p="md" withBorder>
                <Group justify="space-between" wrap="nowrap">
                  <Group gap="md" wrap="nowrap">
                    <ThemeIcon variant="light" size="lg">
                      <tutorial.icon size={20} />
                    </ThemeIcon>
                    <div>
                      <Group gap="xs" mb={4}>
                        <Text fw={600} size="sm">{tutorial.title}</Text>
                        <Badge size="xs" variant="dot" color={
                          tutorial.difficulty === 'Beginner' ? 'green' :
                          tutorial.difficulty === 'Intermediate' ? 'yellow' : 'red'
                        }>
                          {tutorial.difficulty}
                        </Badge>
                        <Badge size="xs" variant="outline">{tutorial.time}</Badge>
                      </Group>
                      <Text size="xs" c="dimmed">{tutorial.description}</Text>
                    </div>
                  </Group>
                  <Button
                    size="xs"
                    variant="light"
                    onClick={() => {
                      onStartTutorial(tutorial.prompt);
                      handleClose();
                    }}
                  >
                    Start
                  </Button>
                </Group>
              </Paper>
            ))}
          </Stack>
        </div>

        <Divider />

        {/* Essential Tips */}
        <Accordion>
          <Accordion.Item value="tips">
            <Accordion.Control icon={<IconBulb size={20} />}>
              Essential Tips for Success
            </Accordion.Control>
            <Accordion.Panel>
              <List size="sm" spacing="xs">
                <List.Item>
                  <strong>Click the robot icon 🤖</strong> to open the AI assistant anytime
                </List.Item>
                <List.Item>
                  <strong>Be specific</strong> when asking the AI for help
                </List.Item>
                <List.Item>
                  <strong>Click any js object</strong> to open the AI-powered code editor
                </List.Item>
                <List.Item>
                  <strong>Use Cmd+Shift+O</strong> to browse all Max objects
                </List.Item>
                <List.Item>
                  <strong>Start simple</strong> and build complexity gradually
                </List.Item>
              </List>
            </Accordion.Panel>
          </Accordion.Item>

          <Accordion.Item value="keyboard">
            <Accordion.Control>Keyboard Shortcuts</Accordion.Control>
            <Accordion.Panel>
              <Stack gap="xs">
                <Group justify="space-between">
                  <Text size="sm">Search Devices</Text>
                  <Code>Cmd/Ctrl + F</Code>
                </Group>
                <Group justify="space-between">
                  <Text size="sm">Object Browser</Text>
                  <Code>Cmd/Ctrl + Shift + O</Code>
                </Group>
                <Group justify="space-between">
                  <Text size="sm">Zoom In/Out</Text>
                  <Code>Cmd/Ctrl + =/-</Code>
                </Group>
                <Group justify="space-between">
                  <Text size="sm">Reset Zoom</Text>
                  <Code>Cmd/Ctrl + R</Code>
                </Group>
              </Stack>
            </Accordion.Panel>
          </Accordion.Item>
        </Accordion>

        {/* Actions */}
        <Group justify="space-between">
          <Button
            variant="subtle"
            onClick={() => {
              setDontShowAgain(!dontShowAgain);
            }}
          >
            {dontShowAgain ? <IconCheck size={16} /> : <IconX size={16} />}
            <Text ml="xs" size="sm">Don't show this again</Text>
          </Button>
          <Group gap="xs">
            <Button variant="default" onClick={handleClose}>
              Skip
            </Button>
            <Button
              onClick={() => {
                onStartTutorial(quickTutorials[0].prompt);
                handleClose();
              }}
            >
              Start Tutorial
            </Button>
          </Group>
        </Group>
      </Stack>
    </Modal>
  );
}

// Check if user has dismissed the modal
export function shouldShowGettingStarted() {
  return !localStorage.getItem('m4l_hide_getting_started');
}
