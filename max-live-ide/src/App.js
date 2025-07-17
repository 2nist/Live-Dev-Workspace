import React, { useState } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { CustomMantineProvider } from './theme/MantineProvider';
import { Group, Button, Paper } from '@mantine/core';
import '@xyflow/react/dist/style.css';
import './App.css';

// Import enhanced components
import EnhancedApp from './components/EnhancedApp';
import TestApp from './TestApp';
import MaxObjectNode from './components/MaxObjectNode';
import OriginalApp from './OriginalApp';

const nodeTypes = {
  maxObject: MaxObjectNode,
};

function App() {
  const [mode, setMode] = useState('enhanced'); // 'enhanced', 'test', or 'original'

  return (
    <CustomMantineProvider>
      <div className="App">
        {/* Mode Switcher */}
        <Paper p="md" withBorder radius={0}>
          <Group justify="center">
            <Button
              variant={mode === 'enhanced' ? 'filled' : 'light'}
              onClick={() => setMode('enhanced')}
              leftSection="🚀"
            >
              Enhanced UI
            </Button>
            <Button
              variant={mode === 'test' ? 'filled' : 'light'}
              onClick={() => setMode('test')}
              leftSection="🧪"
            >
              Test Suite
            </Button>
            <Button
              variant={mode === 'original' ? 'filled' : 'light'}
              onClick={() => setMode('original')}
              leftSection="📝"
            >
              Original IDE
            </Button>
          </Group>
        </Paper>

        {/* Content */}
        <div className="app-content">
          <ReactFlowProvider>
            {mode === 'enhanced' && <EnhancedApp nodeTypes={nodeTypes} />}
            {mode === 'test' && <TestApp />}
            {mode === 'original' && <OriginalApp nodeTypes={nodeTypes} />}
          </ReactFlowProvider>
        </div>
      </div>
    </CustomMantineProvider>
  );
}

export default App;
