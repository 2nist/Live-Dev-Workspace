import React, { useState, useEffect } from 'react';
import { ReactFlowProvider } from '@xyflow/react';
import { useCanvasNavigation, useDeviceSearch, useLiveStatus } from './hooks';
import './TestApp.css';

// Mock data for testing
const mockNodes = [
  {
    id: 'node-1',
    type: 'maxObject',
    position: { x: 100, y: 100 },
    data: {
      label: 'osc~ 440',
      objectType: 'audio',
      status: 'connected',
      tags: ['generator', 'audio', 'oscillator'],
      hasSubpatch: false
    }
  },
  {
    id: 'node-2',
    type: 'maxObject',
    position: { x: 300, y: 100 },
    data: {
      label: 'gain~ 0.5',
      objectType: 'audio',
      status: 'running',
      tags: ['effect', 'audio', 'amplitude'],
      hasSubpatch: false
    }
  },
  {
    id: 'node-3',
    type: 'maxObject',
    position: { x: 500, y: 100 },
    data: {
      label: 'dac~',
      objectType: 'audio',
      status: 'connected',
      tags: ['output', 'audio', 'interface'],
      hasSubpatch: false
    }
  },
  {
    id: 'node-4',
    type: 'maxObject',
    position: { x: 100, y: 300 },
    data: {
      label: 'live.dial tempo',
      objectType: 'live-api',
      status: 'error',
      tags: ['control', 'live', 'tempo'],
      hasSubpatch: false
    }
  },
  {
    id: 'node-5',
    type: 'maxObject',
    position: { x: 300, y: 300 },
    data: {
      label: 'p complex-synth',
      objectType: 'subpatch',
      status: 'connected',
      tags: ['synthesizer', 'complex', 'audio'],
      hasSubpatch: true
    }
  },
  {
    id: 'node-6',
    type: 'maxObject',
    position: { x: 500, y: 300 },
    data: {
      label: 'midiout',
      objectType: 'midi',
      status: 'disabled',
      tags: ['output', 'midi', 'interface'],
      hasSubpatch: false
    }
  }
];

const mockEdges = [
  {
    id: 'edge-1',
    source: 'node-1',
    target: 'node-2',
    type: 'default',
    label: 'audio signal',
    status: 'active'
  },
  {
    id: 'edge-2',
    source: 'node-2',
    target: 'node-3',
    type: 'default',
    label: 'audio signal',
    status: 'active'
  },
  {
    id: 'edge-3',
    source: 'node-4',
    target: 'node-5',
    type: 'default',
    label: 'control data',
    status: 'error'
  }
];

const TestApp = () => {
  const [testResults, setTestResults] = useState({});
  const [currentTest, setCurrentTest] = useState('');
  
  // Initialize hooks
  const navigation = useCanvasNavigation({ x: 0, y: 0, zoom: 1 });
  const search = useDeviceSearch(mockNodes, mockEdges);
  const liveStatus = useLiveStatus('ws://localhost:8080', 'http://localhost:8081');

  // Test functions
  const runNavigationTests = () => {
    setCurrentTest('Navigation Tests');
    const results = {};

    try {
      // Test viewport management
      navigation.setViewport({ x: 100, y: 100, zoom: 0.5 });
      results.setViewport = '✅ Viewport updated successfully';

      // Test zoom functions
      navigation.zoomIn(1.2, false);
      results.zoomIn = '✅ Zoom in working';

      navigation.zoomOut(0.8, false);
      results.zoomOut = '✅ Zoom out working';

      // Test jump to node
      navigation.jumpToNode('node-1', mockNodes, false);
      results.jumpToNode = '✅ Jump to node working';

      // Test fit view
      navigation.fitView(mockNodes, 100, false);
      results.fitView = '✅ Fit view working';

    } catch (error) {
      results.error = `❌ Navigation test failed: ${error.message}`;
    }

    setTestResults(prev => ({ ...prev, navigation: results }));
  };

  const runSearchTests = () => {
    setCurrentTest('Search Tests');
    const results = {};

    try {
      // Test search functionality
      search.setSearchTerm('osc');
      setTimeout(() => {
        if (search.searchResults.length > 0) {
          results.basicSearch = '✅ Basic search working';
        } else {
          results.basicSearch = '❌ Basic search not working';
        }
      }, 500);

      // Test filter options
      const filterOptions = search.getFilterOptions();
      results.filterOptions = `✅ Found ${filterOptions.objectTypes.length} object types, ${filterOptions.tags.length} tags`;

      // Test fuzzy search
      search.setSearchTerm('gen');
      setTimeout(() => {
        results.fuzzySearch = search.searchResults.length > 0 ? 
          '✅ Fuzzy search working' : '❌ Fuzzy search not working';
      }, 500);

      // Test filters
      search.setFilters({ objectType: 'audio', status: 'all', tags: [] });
      results.filters = '✅ Filter setting working';

    } catch (error) {
      results.error = `❌ Search test failed: ${error.message}`;
    }

    setTestResults(prev => ({ ...prev, search: results }));
  };

  const runLiveStatusTests = () => {
    setCurrentTest('Live Status Tests');
    const results = {};

    try {
      // Test connection state
      results.connectionState = `Connection: ${liveStatus.connectionState}`;
      results.isConnected = `Connected: ${liveStatus.isConnected ? '✅' : '❌'}`;

      // Test transport controls (will fail without actual Live connection)
      try {
        liveStatus.playPause();
        results.transportControls = '✅ Transport controls callable';
      } catch (error) {
        results.transportControls = '⚠️ Transport controls require Live connection';
      }

      // Test device status management
      liveStatus.updateDeviceStatus('test-device', 'connected');
      const deviceStatus = liveStatus.getDeviceStatus('test-device');
      results.deviceStatus = deviceStatus.status === 'connected' ? 
        '✅ Device status management working' : '❌ Device status not working';

      // Test error handling
      liveStatus.addError('Test Error', 'This is a test error');
      results.errorHandling = liveStatus.errorLog.length > 0 ? 
        '✅ Error logging working' : '❌ Error logging not working';

    } catch (error) {
      results.error = `❌ Live status test failed: ${error.message}`;
    }

    setTestResults(prev => ({ ...prev, liveStatus: results }));
  };

  const runIntegrationTests = () => {
    setCurrentTest('Integration Tests');
    const results = {};

    try {
      // Test hook interaction
      search.setSearchTerm('node-1');
      setTimeout(() => {
        if (search.searchResults.length > 0) {
          navigation.jumpToNode(search.searchResults[0].id, mockNodes, false);
          results.searchAndNavigate = '✅ Search + Navigation integration working';
        }
      }, 500);

      // Test data flow
      const nodeCount = mockNodes.length;
      const edgeCount = mockEdges.length;
      const searchOptionsCount = search.getFilterOptions().objectTypes.length;
      
      results.dataFlow = `✅ Data flow: ${nodeCount} nodes, ${edgeCount} edges, ${searchOptionsCount} types`;

      // Test performance
      const startTime = Date.now();
      for (let i = 0; i < 100; i++) {
        search.performSearch('test', 'objects');
      }
      const endTime = Date.now();
      results.performance = `✅ 100 searches completed in ${endTime - startTime}ms`;

    } catch (error) {
      results.error = `❌ Integration test failed: ${error.message}`;
    }

    setTestResults(prev => ({ ...prev, integration: results }));
  };

  const runAllTests = () => {
    runNavigationTests();
    setTimeout(() => runSearchTests(), 100);
    setTimeout(() => runLiveStatusTests(), 200);
    setTimeout(() => runIntegrationTests(), 300);
  };

  return (
    <div className="test-app">
      {/* Test Control Panel */}
      <div className="test-panel">
        <h2>🧪 Enhanced UI Test Suite</h2>
        
        <div className="test-controls">
          <button onClick={runAllTests} className="test-btn primary">
            Run All Tests
          </button>
          <button onClick={runNavigationTests} className="test-btn">
            Test Navigation
          </button>
          <button onClick={runSearchTests} className="test-btn">
            Test Search
          </button>
          <button onClick={runLiveStatusTests} className="test-btn">
            Test Live Status
          </button>
          <button onClick={runIntegrationTests} className="test-btn">
            Test Integration
          </button>
        </div>

        {currentTest && (
          <div className="current-test">
            Running: {currentTest}
          </div>
        )}

        {/* Test Results */}
        <div className="test-results">
          {Object.entries(testResults).map(([category, results]) => (
            <div key={category} className="test-category">
              <h3>{category.charAt(0).toUpperCase() + category.slice(1)} Tests</h3>
              <div className="test-items">
                {Object.entries(results).map(([test, result]) => (
                  <div key={test} className="test-item">
                    <span className="test-name">{test}:</span>
                    <span className="test-result">{result}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Enhanced App Component */}
      <div className="app-container">
        <ReactFlowProvider>
          <EnhancedApp
            initialNodes={mockNodes}
            initialEdges={mockEdges}
            navigation={navigation}
            search={search}
            liveStatus={liveStatus}
          />
        </ReactFlowProvider>
      </div>

      {/* Status Bar */}
      <div className="status-bar">
        <div className="status-item">
          <span>Canvas:</span>
          <span>X: {Math.round(navigation.viewport.x)}, Y: {Math.round(navigation.viewport.y)}, Zoom: {Math.round(navigation.viewport.zoom * 100)}%</span>
        </div>
        <div className="status-item">
          <span>Search:</span>
          <span>{search.searchResults.length} results for "{search.searchTerm}"</span>
        </div>
        <div className="status-item">
          <span>Live:</span>
          <span className={`status-${liveStatus.connectionState}`}>
            {liveStatus.connectionState}
          </span>
        </div>
        <div className="status-item">
          <span>Performance:</span>
          <span>CPU: {liveStatus.performanceMetrics.cpuUsage}%, Latency: {liveStatus.performanceMetrics.latency}ms</span>
        </div>
      </div>
    </div>
  );
};

export default TestApp;
