import React, { useState, useCallback } from 'react';
import { ReactFlow, Background, Controls, MiniMap, useNodesState, useEdgesState, addEdge } from '@xyflow/react';
import { Group, Button, Paper, Text, Badge, Title } from '@mantine/core';
import { IconSearch, IconDevices, IconInfoCircle, IconBook, IconTemplate } from '@tabler/icons-react';
import { useCanvasNavigation, useDeviceSearch, useLiveStatus } from '../hooks';
import { useObjectTemplateBrowser, useObjectBrowserShortcuts, useObjectInsertion } from '../hooks/useObjectTemplateBrowser';
import SearchPanel from './SearchPanel';
import LiveStatusPanel from './LiveStatusPanel';
import DeviceManager from './DeviceManager';
import ObjectTemplateBrowser from './ObjectTemplateBrowser';
import '@xyflow/react/dist/style.css';
import './EnhancedApp.css';

// Mock initial nodes and edges
const initialNodes = [
  {
    id: 'node-1',
    type: 'maxObject',
    position: { x: 250, y: 100 },
    data: { 
      label: 'metro 500',
      objectType: 'utility',
      status: 'connected',
      tags: ['timing', 'metronome', 'utility']
    }
  },
  {
    id: 'node-2',
    type: 'maxObject',
    position: { x: 250, y: 200 },
    data: { 
      label: 'random 100',
      objectType: 'utility',
      status: 'running',
      tags: ['random', 'generator', 'utility']
    }
  },
  {
    id: 'node-3',
    type: 'maxObject',
    position: { x: 400, y: 150 },
    data: { 
      label: 'osc~ 440',
      objectType: 'audio',
      status: 'connected',
      tags: ['oscillator', 'audio', 'generator']
    }
  },
  {
    id: 'node-4',
    type: 'maxObject',
    position: { x: 550, y: 150 },
    data: { 
      label: 'gain~ 0.5',
      objectType: 'audio',
      status: 'running',
      tags: ['gain', 'audio', 'amplifier']
    }
  }
];

const initialEdges = [
  {
    id: 'edge-1',
    source: 'node-1',
    target: 'node-2',
    sourceHandle: 'bottom',
    targetHandle: 'top'
  },
  {
    id: 'edge-2',
    source: 'node-2',
    target: 'node-3',
    sourceHandle: 'bottom',
    targetHandle: 'top'
  },
  {
    id: 'edge-3',
    source: 'node-3',
    target: 'node-4',
    sourceHandle: 'bottom',
    targetHandle: 'top'
  }
];

const EnhancedApp = ({ nodeTypes }) => {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [isSearchOpen, setIsSearchOpen] = useState(false);

  // Object & Template Browser
  const browserControls = useObjectTemplateBrowser();
  const { insertObject, insertTemplate } = useObjectInsertion(setNodes, setEdges);
  
  // Setup keyboard shortcuts for browser
  useObjectBrowserShortcuts(browserControls);

  // Use custom hooks
  const {
    viewport,
    setViewport,
    zoomIn,
    zoomOut,
    resetZoom,
    jumpToNode
  } = useCanvasNavigation();

  const {
    searchTerm,
    setSearchTerm,
    searchResults,
    filteredResults,
    selectedDevice,
    searchHistory,
    clearSearch
  } = useDeviceSearch(nodes, edges);

  const {
    isConnected,
    connectionStatus,
    liveData,
    transportState,
    playPause,
    stop,
    record
  } = useLiveStatus();

  const onConnect = useCallback(
    (params) => setEdges((eds) => addEdge(params, eds)),
    [setEdges]
  );

  const handleDeviceAdd = useCallback((device) => {
    const newNode = {
      id: `node-${Date.now()}`,
      type: 'maxObject',
      position: { x: Math.random() * 500, y: Math.random() * 500 },
      data: { label: device.name || device.objectName }
    };
    setNodes((nds) => [...nds, newNode]);
    setIsSearchOpen(false);
  }, [setNodes]);

  // Handle object and template selection from browser
  const handleObjectSelect = useCallback((object) => {
    const position = { 
      x: viewport.x + 300, 
      y: viewport.y + 200 
    };
    const newNode = insertObject(object, position);
    browserControls.addToRecent(object);
    browserControls.closeBrowser();
    console.log('Added object:', object.name, 'at position:', position);
  }, [insertObject, browserControls, viewport]);

  const handleTemplateSelect = useCallback((template) => {
    const position = { 
      x: viewport.x + 200, 
      y: viewport.y + 100 
    };
    const result = insertTemplate(template, position);
    browserControls.addToRecent(template);
    browserControls.closeBrowser();
    console.log('Added template:', template.name, 'with', result?.nodes?.length, 'nodes');
  }, [insertTemplate, browserControls, viewport]);

  const handleKeyDown = useCallback((event) => {
    if (event.ctrlKey || event.metaKey) {
      switch (event.key) {
        case 'f':
          event.preventDefault();
          setIsSearchOpen(true);
          break;
        case 'o':
          if (event.shiftKey) {
            event.preventDefault();
            browserControls.openBrowser();
          }
          break;
        case '=':
        case '+':
          event.preventDefault();
          zoomIn();
          break;
        case '-':
          event.preventDefault();
          zoomOut();
          break;
        case 'r':
          event.preventDefault();
          resetZoom();
          break;
        default:
          break;
      }
    }
    
    if (event.key === 'Escape') {
      if (isSearchOpen) {
        setIsSearchOpen(false);
      }
      if (browserControls.isOpen) {
        browserControls.closeBrowser();
      }
    }
  }, [zoomIn, zoomOut, resetZoom, browserControls, isSearchOpen]);

  React.useEffect(() => {
    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [handleKeyDown]);

  return (
    <div className="enhanced-app">
      {/* Header with controls */}
      <Paper p="md" withBorder radius={0} mb="md">
        <Group justify="space-between" align="center">
          <Group align="center">
            <Title order={3} c="orange.5">Max Live IDE - Enhanced</Title>
            <Button
              variant="light"
              leftSection={<IconSearch size={16} />}
              onClick={() => setIsSearchOpen(!isSearchOpen)}
              size="sm"
            >
              Search Devices (Ctrl+F)
            </Button>
            <Button
              variant="light"
              leftSection={<IconBook size={16} />}
              onClick={browserControls.openBrowser}
              size="sm"
            >
              Object Browser (Ctrl+Shift+O)
            </Button>
          </Group>
          <LiveStatusPanel 
            isConnected={isConnected}
            connectionStatus={connectionStatus}
            liveData={liveData}
            transportState={transportState}
            onPlay={playPause}
            onStop={stop}
            onRecord={record}
          />
        </Group>
      </Paper>

      {/* Main content area */}
      <div className="enhanced-content">
        {/* Search Panel */}
        {isSearchOpen && (
          <SearchPanel 
            searchTerm={searchTerm}
            onSearch={setSearchTerm}
            searchResults={searchResults}
            onJumpTo={(nodeId) => jumpToNode(nodeId, nodes)}
            onClose={() => setIsSearchOpen(false)}
            nodes={nodes}
          />
        )}

        {/* React Flow Canvas */}
        <div className="flow-container">
          <ReactFlow
            nodes={nodes}
            edges={edges}
            onNodesChange={onNodesChange}
            onEdgesChange={onEdgesChange}
            onConnect={onConnect}
            nodeTypes={nodeTypes}
            viewport={viewport}
            onViewportChange={setViewport}
            fitView
          >
            <Background />
            <Controls />
            <MiniMap 
              nodeStrokeColor="#333"
              nodeColor="#fff"
              nodeBorderRadius={4}
            />
          </ReactFlow>
        </div>

        {/* Object & Template Browser */}
        <ObjectTemplateBrowser
          isVisible={browserControls.isOpen}
          onObjectSelect={handleObjectSelect}
          onTemplateSelect={handleTemplateSelect}
          onClose={browserControls.closeBrowser}
        />

        {/* Device Manager Panel */}
        <DeviceManager 
          nodes={nodes}
          onNodeFocus={(nodeId) => jumpToNode(nodeId, nodes)}
          onNodeDelete={(nodeId) => 
            setNodes((nds) => nds.filter((n) => n.id !== nodeId))
          }
        />
      </div>

      {/* Status Bar */}
      <div className="enhanced-status-bar">
        <span>Nodes: {nodes.length}</span>
        <span>Edges: {edges.length}</span>
        <span>Zoom: {Math.round(viewport.zoom * 100)}%</span>
        <span className={`connection-status ${isConnected ? 'connected' : 'disconnected'}`}>
          Live: {isConnected ? 'Connected' : 'Disconnected'}
        </span>
      </div>
    </div>
  );
};

export default EnhancedApp;
