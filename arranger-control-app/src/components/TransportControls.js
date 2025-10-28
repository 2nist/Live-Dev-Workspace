import { Group, Button, Slider, Text, Stack, Paper } from '@mantine/core';
import { IconPlayerPlay, IconPlayerStop } from '@tabler/icons-react';
import { useState } from 'react';

function TransportControls({ client, connected, currentTempo }) {
  const [tempo, setTempo] = useState(currentTempo);

  const handlePlay = async () => {
    await client.play();
  };

  const handleStop = async () => {
    await client.stop();
  };

  const handleTempoChange = async (value) => {
    setTempo(value);
    await client.setTempo(value);
  };

  // Update local tempo when prop changes
  if (tempo !== currentTempo && currentTempo !== undefined) {
    setTempo(currentTempo);
  }

  return (
    <Paper shadow="sm" p="md" mb="md" withBorder>
      <Stack gap="md">
        <Text size="lg" fw={600}>Transport</Text>
        
        <Group gap="sm">
          <Button
            leftSection={<IconPlayerPlay size={16} />}
            onClick={handlePlay}
            disabled={!connected}
            color="green"
          >
            Play
          </Button>
          <Button
            leftSection={<IconPlayerStop size={16} />}
            onClick={handleStop}
            disabled={!connected}
            color="red"
          >
            Stop
          </Button>
        </Group>

        <div>
          <Text size="sm" mb="xs">
            Tempo: {tempo} BPM
          </Text>
          <Slider
            value={tempo}
            onChange={handleTempoChange}
            min={60}
            max={180}
            step={1}
            disabled={!connected}
            marks={[
              { value: 60, label: '60' },
              { value: 120, label: '120' },
              { value: 180, label: '180' }
            ]}
          />
        </div>
      </Stack>
    </Paper>
  );
}

export default TransportControls;
