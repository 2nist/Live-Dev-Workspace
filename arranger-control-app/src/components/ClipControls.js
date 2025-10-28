import { Button, Text, Stack, Paper, Group, NumberInput } from '@mantine/core';
import { IconPlus, IconMusic } from '@tabler/icons-react';
import { useState } from 'react';

function ClipControls({ client, connected }) {
  const [trackIndex, setTrackIndex] = useState(0);
  const [sceneIndex, setSceneIndex] = useState(0);
  const [clipLength, setClipLength] = useState(4.0);

  const handleCreateClip = async () => {
    const result = await client.createClip(trackIndex, sceneIndex, clipLength);
    console.log('Clip created:', result);
  };

  return (
    <Paper shadow="sm" p="md" mb="md" withBorder>
      <Stack gap="md">
        <Text size="lg" fw={600}>Clips</Text>
        
        <Group gap="sm" grow>
          <NumberInput
            label="Track"
            value={trackIndex}
            onChange={(val) => setTrackIndex(val || 0)}
            min={0}
            max={999}
            disabled={!connected}
          />
          <NumberInput
            label="Scene"
            value={sceneIndex}
            onChange={(val) => setSceneIndex(val || 0)}
            min={0}
            max={999}
            disabled={!connected}
          />
          <NumberInput
            label="Length (bars)"
            value={clipLength}
            onChange={(val) => setClipLength(val || 4.0)}
            min={1}
            max={64}
            step={0.5}
            disabled={!connected}
          />
        </Group>

        <Button
          leftSection={<IconPlus size={16} />}
          onClick={handleCreateClip}
          disabled={!connected}
          variant="light"
          fullWidth
        >
          Create Clip
        </Button>
      </Stack>
    </Paper>
  );
}

export default ClipControls;
