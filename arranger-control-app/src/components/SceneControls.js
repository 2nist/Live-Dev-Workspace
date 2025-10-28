import { Button, Text, Stack, Paper, Group, NumberInput } from '@mantine/core';
import { IconPlus, IconPlayerPlay } from '@tabler/icons-react';
import { useState } from 'react';

function SceneControls({ client, connected }) {
  const [sceneIndex, setSceneIndex] = useState(0);

  const handleCreateScene = async () => {
    const result = await client.createScene();
    console.log('Scene created:', result);
  };

  const handleTriggerScene = async () => {
    const result = await client.triggerScene(sceneIndex);
    console.log('Scene triggered:', result);
  };

  return (
    <Paper shadow="sm" p="md" mb="md" withBorder>
      <Stack gap="md">
        <Text size="lg" fw={600}>Scenes</Text>
        
        <Group gap="sm">
          <Button
            leftSection={<IconPlus size={16} />}
            onClick={handleCreateScene}
            disabled={!connected}
            variant="light"
          >
            Create Scene
          </Button>
        </Group>

        <Group gap="sm" align="flex-end">
          <NumberInput
            label="Scene Index"
            value={sceneIndex}
            onChange={(val) => setSceneIndex(val || 0)}
            min={0}
            max={999}
            style={{ flex: 1 }}
            disabled={!connected}
          />
          <Button
            leftSection={<IconPlayerPlay size={16} />}
            onClick={handleTriggerScene}
            disabled={!connected}
          >
            Trigger
          </Button>
        </Group>
      </Stack>
    </Paper>
  );
}

export default SceneControls;
