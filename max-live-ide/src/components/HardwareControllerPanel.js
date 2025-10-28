import React, { useState, useEffect } from 'react';
import {
  Paper,
  Title,
  Group,
  Stack,
  Button,
  Select,
  Badge,
  Card,
  Text,
  Switch,
  Grid,
  ActionIcon,
  Tooltip,
  Divider,
  Alert
} from '@mantine/core';
import {
  IconDeviceGamepad2,
  IconPlug,
  IconPlugOff,
  IconRefresh,
  IconMusic,
  IconLayoutGrid,
  IconPiano,
  IconCheck,
  IconAlertCircle
} from '@tabler/icons-react';
import ArrangerOSC from '../utils/ArrangerOSC';

/**
 * Hardware Controller Panel for Max Live IDE
 * 
 * Integrates Ableton hardware controllers (Push, Launchpad, etc.)
 * with the arranger system and Max IDE.
 */
const HardwareControllerPanel = ({ currentArrangement, currentProgression }) => {
  const [controllers, setControllers] = useState([]);
  const [detectedControllers, setDetectedControllers] = useState([]);
  const [selectedController, setSelectedController] = useState(null);
  const [controllerMode, setControllerMode] = useState('chord');
  const [isConnecting, setIsConnecting] = useState(false);
  const [error, setError] = useState(null);
  const [syncEnabled, setSyncEnabled] = useState(true);

  // Initialize - detect controllers
  useEffect(() => {
    detectControllers();
    listControllers();
  }, []);

  // Sync current progression/arrangement to hardware
  useEffect(() => {
    if (!syncEnabled || !hasActiveController()) return;

    if (controllerMode === 'chord' && currentProgression) {
      displayProgressionOnHardware(currentProgression);
    } else if (controllerMode === 'section' && currentArrangement) {
      displayArrangementOnHardware(currentArrangement);
    }
  }, [currentProgression, currentArrangement, controllerMode, syncEnabled]);

  /**
   * Detect connected hardware controllers
   */
  const detectControllers = async () => {
    try {
      const result = await ArrangerOSC.sendHardwareCommand('detect');
      if (result && result.detected) {
        setDetectedControllers(result.detected);
      }
    } catch (err) {
      console.error('Failed to detect controllers:', err);
      setError('Failed to detect controllers');
    }
  };

  /**
   * List already connected controllers
   */
  const listControllers = async () => {
    try {
      const result = await ArrangerOSC.sendHardwareCommand('list');
      if (result && result.controllers) {
        setControllers(result.controllers);
      }
    } catch (err) {
      console.error('Failed to list controllers:', err);
    }
  };

  /**
   * Connect to a hardware controller
   */
  const connectController = async (controllerInfo) => {
    setIsConnecting(true);
    setError(null);

    try {
      const result = await ArrangerOSC.sendHardwareCommand('connect', {
        type: controllerInfo.name,
        midiIn: controllerInfo.port,
        midiOut: controllerInfo.port // Assume same port for in/out
      });

      if (result && result.status === 'connected') {
        await listControllers();
        setSelectedController(controllerInfo.name);
      }
    } catch (err) {
      console.error('Failed to connect controller:', err);
      setError(`Failed to connect to ${controllerInfo.type}`);
    } finally {
      setIsConnecting(false);
    }
  };

  /**
   * Disconnect a controller
   */
  const disconnectController = async (name) => {
    try {
      await ArrangerOSC.sendHardwareCommand('disconnect', { name });
      await listControllers();
      if (selectedController === name) {
        setSelectedController(null);
      }
    } catch (err) {
      console.error('Failed to disconnect controller:', err);
    }
  };

  /**
   * Change controller mode (chord/section/scale)
   */
  const changeMode = async (mode) => {
    try {
      await ArrangerOSC.sendHardwareCommand('set_mode', { mode });
      setControllerMode(mode);
    } catch (err) {
      console.error('Failed to change mode:', err);
    }
  };

  /**
   * Display chord progression on hardware
   */
  const displayProgressionOnHardware = async (progression) => {
    try {
      await ArrangerOSC.sendHardwareCommand('display_progression', {
        chords: progression
      });
    } catch (err) {
      console.error('Failed to display progression:', err);
    }
  };

  /**
   * Display arrangement on hardware
   */
  const displayArrangementOnHardware = async (arrangement) => {
    try {
      await ArrangerOSC.sendHardwareCommand('display_arrangement', {
        arrangement: arrangement
      });
    } catch (err) {
      console.error('Failed to display arrangement:', err);
    }
  };

  /**
   * Highlight a chord on the controller
   */
  const highlightChord = async (chordIndex) => {
    try {
      await ArrangerOSC.sendHardwareCommand('highlight_chord', {
        index: chordIndex
      });
    } catch (err) {
      console.error('Failed to highlight chord:', err);
    }
  };

  /**
   * Check if any controller is active
   */
  const hasActiveController = () => {
    return controllers.some(c => c.connected);
  };

  /**
   * Get controller type icon
   */
  const getControllerIcon = (type) => {
    if (type.includes('push')) return <IconDeviceGamepad2 size={20} />;
    if (type.includes('launchpad')) return <IconLayoutGrid size={20} />;
    if (type.includes('apc')) return <IconPiano size={20} />;
    return <IconPiano size={20} />;
  };

  /**
   * Get controller status badge
   */
  const getStatusBadge = (controller) => {
    return controller.connected ? (
      <Badge color="green" leftSection={<IconCheck size={14} />}>
        Connected
      </Badge>
    ) : (
      <Badge color="gray">
        Disconnected
      </Badge>
    );
  };

  return (
    <Paper p="md" withBorder style={{ height: '100%' }}>
      <Stack spacing="md">
        {/* Header */}
        <Group position="apart">
          <Group spacing="xs">
            <IconDeviceGamepad2 size={24} />
            <Title order={4}>Hardware Controllers</Title>
          </Group>
          <Group spacing="xs">
            <Tooltip label="Refresh controllers">
              <ActionIcon
                variant="light"
                onClick={() => {
                  detectControllers();
                  listControllers();
                }}
              >
                <IconRefresh size={18} />
              </ActionIcon>
            </Tooltip>
            <Switch
              label="Auto-sync"
              checked={syncEnabled}
              onChange={(e) => setSyncEnabled(e.currentTarget.checked)}
              size="sm"
            />
          </Group>
        </Group>

        {/* Error Alert */}
        {error && (
          <Alert
            icon={<IconAlertCircle size={16} />}
            color="red"
            title="Error"
            withCloseButton
            onClose={() => setError(null)}
          >
            {error}
          </Alert>
        )}

        {/* Detected Controllers */}
        {detectedControllers.length > 0 && (
          <>
            <Divider label="Detected Controllers" />
            <Grid>
              {detectedControllers.map((detected, idx) => (
                <Grid.Col span={6} key={idx}>
                  <Card withBorder padding="sm">
                    <Stack spacing="xs">
                      <Group position="apart">
                        {getControllerIcon(detected.type)}
                        <Text size="sm" weight={500}>
                          {detected.type}
                        </Text>
                      </Group>
                      <Text size="xs" color="dimmed" lineClamp={1}>
                        {detected.port}
                      </Text>
                      <Button
                        size="xs"
                        leftIcon={<IconPlug size={14} />}
                        onClick={() => connectController(detected)}
                        loading={isConnecting}
                        fullWidth
                      >
                        Connect
                      </Button>
                    </Stack>
                  </Card>
                </Grid.Col>
              ))}
            </Grid>
          </>
        )}

        {/* Connected Controllers */}
        {controllers.length > 0 && (
          <>
            <Divider label="Connected Controllers" />
            <Stack spacing="xs">
              {controllers.map((controller, idx) => (
                <Card key={idx} withBorder padding="md">
                  <Group position="apart">
                    <Group>
                      {getControllerIcon(controller.type)}
                      <Stack spacing={0}>
                        <Text weight={500}>{controller.name}</Text>
                        <Text size="xs" color="dimmed">
                          {controller.capabilities.pads} pads
                          {controller.capabilities.encoders > 0 &&
                            `, ${controller.capabilities.encoders} encoders`}
                        </Text>
                      </Stack>
                    </Group>
                    <Group spacing="xs">
                      {getStatusBadge(controller)}
                      <ActionIcon
                        color="red"
                        variant="light"
                        onClick={() => disconnectController(controller.name)}
                      >
                        <IconPlugOff size={18} />
                      </ActionIcon>
                    </Group>
                  </Group>
                </Card>
              ))}
            </Stack>
          </>
        )}

        {/* Controller Mode Selection */}
        {hasActiveController() && (
          <>
            <Divider label="Controller Mode" />
            <Select
              label="Display Mode"
              value={controllerMode}
              onChange={changeMode}
              data={[
                {
                  value: 'chord',
                  label: '🎵 Chord Progression',
                  icon: <IconMusic size={16} />
                },
                {
                  value: 'section',
                  label: '📋 Arrangement Sections',
                  icon: <IconLayoutGrid size={16} />
                },
                {
                  value: 'scale',
                  label: '🎹 Scale Layout',
                  icon: <IconPiano size={16} />
                }
              ]}
            />
          </>
        )}

        {/* No Controllers State */}
        {controllers.length === 0 && detectedControllers.length === 0 && (
          <Card withBorder padding="xl">
            <Stack align="center" spacing="md">
              <IconDeviceGamepad2 size={48} stroke={1} style={{ opacity: 0.3 }} />
              <Text color="dimmed" align="center">
                No hardware controllers detected
              </Text>
              <Text size="xs" color="dimmed" align="center">
                Connect an Ableton Push, Launchpad, or other MIDI controller
              </Text>
              <Button
                variant="light"
                leftIcon={<IconRefresh size={16} />}
                onClick={detectControllers}
              >
                Scan for Controllers
              </Button>
            </Stack>
          </Card>
        )}
      </Stack>
    </Paper>
  );
};

export default HardwareControllerPanel;
