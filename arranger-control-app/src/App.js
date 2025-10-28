import { useState, useEffect } from 'react';
import { MantineProvider, AppShell, Container, Title, Badge } from '@mantine/core';
import TransportControls from './components/TransportControls';
import SceneControls from './components/SceneControls';
import ClipControls from './components/ClipControls';
import TrackControls from './components/TrackControls';
import ArrangerOSCClient from './ArrangerOSC';

import '@mantine/core/styles.css';

function App() {
  const [client] = useState(() => new ArrangerOSCClient({
    host: 'localhost',
    port: 12000,
    onStatusChange: (connected) => setConnected(connected)
  }));
  const [connected, setConnected] = useState(false);
  const [tempo, setTempo] = useState(120);

  useEffect(() => {
    // Connect on mount
    client.connect();

    // Disconnect on unmount
    return () => {
      client.disconnect();
    };
  }, [client]);

  // Poll tempo periodically
  useEffect(() => {
    if (!connected) return;

    const pollTempo = async () => {
      const result = await client.getTempo();
      if (result && result.tempo !== undefined) {
        setTempo(result.tempo);
      }
    };

    pollTempo();
    const interval = setInterval(pollTempo, 2000);

    return () => clearInterval(interval);
  }, [connected, client]);

  return (
    <MantineProvider theme={{ colorScheme: 'dark' }}>
      <AppShell
        padding="md"
        header={{ height: 60 }}
        styles={(theme) => ({
          main: { backgroundColor: theme.colors.dark[8] }
        })}
      >
        <AppShell.Header style={{ 
          display: 'flex', 
          alignItems: 'center', 
          paddingLeft: '1rem',
          paddingRight: '1rem',
          justifyContent: 'space-between'
        }}>
          <Title order={3}>Arranger Control</Title>
          <Badge 
            color={connected ? 'green' : 'red'} 
            variant="filled"
            size="lg"
          >
            {connected ? '● Connected' : '● Disconnected'}
          </Badge>
        </AppShell.Header>

        <AppShell.Main>
          <Container size="lg">
            <TransportControls 
              client={client} 
              connected={connected}
              currentTempo={tempo}
            />
            <SceneControls 
              client={client} 
              connected={connected}
            />
            <ClipControls 
              client={client} 
              connected={connected}
            />
            <TrackControls 
              client={client} 
              connected={connected}
            />
          </Container>
        </AppShell.Main>
      </AppShell>
    </MantineProvider>
  );
}

export default App;
