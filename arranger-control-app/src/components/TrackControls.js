import { Slider, Text, Stack, Paper, Group, NumberInput, Switch } from '@mantine/core';
import { useState } from 'react';

function TrackControls({ client, connected }) {
  const [trackIndex, setTrackIndex] = useState(0);
  const [volume, setVolume] = useState(0.85);
  const [pan, setPan] = useState(0.0);
  const [mute, setMute] = useState(false);
  const [solo, setSolo] = useState(false);
  const [arm, setArm] = useState(false);

  const handleVolumeChange = async (value) => {
    setVolume(value);
    await client.setVolume(trackIndex, value);
  };

  const handlePanChange = async (value) => {
    setPan(value);
    await client.setPan(trackIndex, value);
  };

  const handleMuteToggle = async (event) => {
    const newMute = event.currentTarget.checked;
    setMute(newMute);
    await client.setMute(trackIndex, newMute);
  };

  const handleSoloToggle = async (event) => {
    const newSolo = event.currentTarget.checked;
    setSolo(newSolo);
    await client.setSolo(trackIndex, newSolo);
  };

  const handleArmToggle = async (event) => {
    const newArm = event.currentTarget.checked;
    setArm(newArm);
    await client.setArm(trackIndex, newArm);
  };

  return (
    <Paper shadow="sm" p="md" mb="md" withBorder>
      <Stack gap="md">
        <Text size="lg" fw={600}>Track Controls</Text>
        
        <NumberInput
          label="Track Index"
          value={trackIndex}
          onChange={(val) => setTrackIndex(val || 0)}
          min={0}
          max={999}
          disabled={!connected}
        />

        <div>
          <Text size="sm" mb="xs">
            Volume: {(volume * 100).toFixed(0)}%
          </Text>
          <Slider
            value={volume}
            onChange={handleVolumeChange}
            min={0}
            max={1}
            step={0.01}
            disabled={!connected}
            marks={[
              { value: 0, label: '0%' },
              { value: 0.85, label: '85%' },
              { value: 1, label: '100%' }
            ]}
          />
        </div>

        <div>
          <Text size="sm" mb="xs">
            Pan: {pan > 0 ? `${(pan * 100).toFixed(0)}% R` : pan < 0 ? `${Math.abs(pan * 100).toFixed(0)}% L` : 'Center'}
          </Text>
          <Slider
            value={pan}
            onChange={handlePanChange}
            min={-1}
            max={1}
            step={0.01}
            disabled={!connected}
            marks={[
              { value: -1, label: 'L' },
              { value: 0, label: 'C' },
              { value: 1, label: 'R' }
            ]}
          />
        </div>

        <Group gap="md" grow>
          <Switch
            label="Mute"
            checked={mute}
            onChange={handleMuteToggle}
            disabled={!connected}
          />
          <Switch
            label="Solo"
            checked={solo}
            onChange={handleSoloToggle}
            disabled={!connected}
          />
          <Switch
            label="Arm"
            checked={arm}
            onChange={handleArmToggle}
            disabled={!connected}
          />
        </Group>
      </Stack>
    </Paper>
  );
}

export default TrackControls;
