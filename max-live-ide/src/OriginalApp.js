import React, { useCallback, useState, useEffect } from 'react';
import {
  ReactFlow,
  MiniMap,
  Controls,
  Background,
  useNodesState,
  useEdgesState,
  addEdge,
} from '@xyflow/react';

import MaxObjectNode from './components/MaxObjectNode';
import { MaxPatParser } from './utils/MaxPatParser';
import { AbletonLiveAPI, MaxDeviceSync } from './utils/AbletonLiveAPI';

const nodeTypes = {
  maxObject: MaxObjectNode,
};

const initialNodes = [
  {
    id: '1',
    type: 'maxObject',
    position: { x: 250, y: 25 },
    data: { label: 'osc~ 440' },
  },
  {
    id: '2',
    type: 'maxObject', 
    position: { x: 100, y: 125 },
    data: { label: 'gain~ 0.5' },
  },
  {
    id: '3',
    type: 'maxObject',
    position: { x: 250, y: 250 },
    data: { label: 'dac~' },
  },
];

const initialEdges = [
  { id: 'e1-2', source: '1', target: '2' },
  { id: 'e2-3', source: '2', target: '3' },
];

function OriginalApp() {
  const [nodes, setNodes, onNodesChange] = useNodesState(initialNodes);
  const [edges, setEdges, onEdgesChange] = useEdgesState(initialEdges);
  const [currentPatch, setCurrentPatch] = useState(null);
  const [abletonAPI, setAbletonAPI] = useState(null);
  const [deviceSync, setDeviceSync] = useState(null);
  const [isConnected, setIsConnected] = useState(false);
  const [selectedTrack, setSelectedTrack] = useState(0);
  const [selectedDevice, setSelectedDevice] = useState(0);

  // Initialize Ableton Live API
  useEffect(() => {
    const api = new AbletonLiveAPI();
    const sync = new MaxDeviceSync(api);
    
    api.on('connected', () => {
      setIsConnected(true);
      console.log('Connected to Ableton Live');
    });
    
    api.on('disconnected', () => {
      setIsConnected(false);
      console.log('Disconnected from Ableton Live');
    });
    
    api.on('error', (error) => {
      console.error('Ableton Live API error:', error);
      setIsConnected(false);
    });
    
    // Listen for parameter changes from Live
    api.on('patcherParameterChanged', (data) => {
      setNodes(currentNodes => 
        currentNodes.map(node => {
          if (node.id === data.objectId.toString()) {
            return {
              ...node,
              data: {
                ...node.data,
                parameterValue: data.value,
                label: `${node.data.label} (${data.value})`
              }
            };
          }
          return node;
        })
      );
    });
    
    setAbletonAPI(api);
    setDeviceSync(sync);
    
    return () => {
      api.disconnect();
    };
  }, [setNodes]);

  const connectToLive = useCallback(async () => {
    if (abletonAPI) {
      await abletonAPI.connect();
    }
  }, [abletonAPI]);

  const syncWithLive = useCallback(async () => {
    if (deviceSync && currentPatch && isConnected) {
      const success = await deviceSync.syncDevice(currentPatch, selectedTrack, selectedDevice);
      if (success) {
        console.log('Device synced with Live');
      } else {
        console.error('Failed to sync device with Live');
      }
    }
  }, [deviceSync, currentPatch, isConnected, selectedTrack, selectedDevice]);

  const reloadInLive = useCallback(async () => {
    if (deviceSync && isConnected) {
      const deviceId = `${selectedTrack}-${selectedDevice}`;
      const success = await deviceSync.reloadDevice(deviceId);
      if (success) {
        console.log('Device reloaded in Live');
      } else {
        console.error('Failed to reload device in Live');
      }
    }
  }, [deviceSync, isConnected, selectedTrack, selectedDevice]);

  const exportToLive = useCallback(async () => {
    if (currentPatch && abletonAPI && isConnected) {
      try {
        // Update patch with current nodes and edges
        currentPatch.objects = nodes.map(node => {
          const obj = node.data.maxObject || {
            box: {
              id: parseInt(node.id),
              maxclass: 'newobj',
              text: node.data.label,
              patching_rect: [node.position.x, node.position.y, 100, 22],
              numinlets: 1,
              numoutlets: 1
            }
          };
          
          // Update position
          obj.box.patching_rect[0] = node.position.x;
          obj.box.patching_rect[1] = node.position.y;
          obj.box.text = node.data.label;
          
          return obj;
        });
        
        currentPatch.lines = edges.map(edge => ({
          patchline: {
            source: [parseInt(edge.source), parseInt(edge.sourceHandle || 0)],
            destination: [parseInt(edge.target), parseInt(edge.targetHandle || 0)]
          }
        }));
        
        // Export as temp file and load into Live
        const json = MaxPatParser.stringify(currentPatch);
        const blob = new Blob([json], { type: 'application/json' });
        const tempFile = new File([blob], 'temp_device.amxd', { type: 'application/json' });
        
        // Load into Live (this would need backend support)
        await abletonAPI.loadMaxDevice(selectedTrack, tempFile.name);
        console.log('Device exported to Live');
      } catch (error) {
        console.error('Failed to export to Live:', error);
      }
    }
  }, [currentPatch, nodes, edges, abletonAPI, isConnected, selectedTrack]);

  const onConnect = useCallback((params) => setEdges((eds) => addEdge(params, eds)), [setEdges]);

  const handleFileLoad = useCallback((event) => {
    const file = event.target.files[0];
    if (file && file.name.endsWith('.maxpat')) {
      const reader = new FileReader();
      reader.onload = (e) => {
        try {
          const patcher = MaxPatParser.parse(e.target.result);
          setCurrentPatch(patcher);
          
          // Convert Max objects to React Flow nodes
          const newNodes = patcher.objects.map(obj => ({
            id: obj.id.toString(),
            type: 'maxObject',
            position: { 
              x: obj.patching_rect[0] || 0, 
              y: obj.patching_rect[1] || 0 
            },
            data: { 
              label: obj.text || obj.maxclass,
              maxObject: obj
            },
          }));
          
          // Convert Max lines to React Flow edges
          const newEdges = patcher.lines.map((line, index) => ({
            id: `line-${index}`,
            source: line.getSourceId().toString(),
            target: line.getDestinationId().toString(),
            sourceHandle: line.getSourceOutlet().toString(),
            targetHandle: line.getDestinationInlet().toString(),
          }));
          
          setNodes(newNodes);
          setEdges(newEdges);
        } catch (error) {
          console.error('Failed to parse maxpat file:', error);
        }
      };
      reader.readAsText(file);
    }
  }, [setNodes, setEdges]);

  const handleExport = useCallback(() => {
    if (currentPatch) {
      // Update patch with current nodes and edges
      currentPatch.objects = nodes.map(node => {
        const obj = node.data.maxObject || {
          box: {
            id: parseInt(node.id),
            maxclass: 'newobj',
            text: node.data.label,
            patching_rect: [node.position.x, node.position.y, 100, 22],
            numinlets: 1,
            numoutlets: 1
          }
        };
        
        // Update position
        obj.box.patching_rect[0] = node.position.x;
        obj.box.patching_rect[1] = node.position.y;
        obj.box.text = node.data.label;
        
        return obj;
      });
      
      currentPatch.lines = edges.map(edge => ({
        patchline: {
          source: [parseInt(edge.source), parseInt(edge.sourceHandle || 0)],
          destination: [parseInt(edge.target), parseInt(edge.targetHandle || 0)]
        }
      }));
      
      const json = MaxPatParser.stringify(currentPatch);
      const blob = new Blob([json], { type: 'application/json' });
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = 'patch.maxpat';
      a.click();
      URL.revokeObjectURL(url);
    }
  }, [currentPatch, nodes, edges]);

  return (
    <div style={{ width: '100%', height: '100vh' }}>
      <div style={{ position: 'absolute', top: 10, left: 10, zIndex: 1000, background: 'white', padding: 10, borderRadius: 5, boxShadow: '0 2px 4px rgba(0,0,0,0.1)' }}>
        <div style={{ marginBottom: 10 }}>
          <input
            type="file"
            accept=".maxpat,.amxd"
            onChange={handleFileLoad}
            style={{ marginRight: 10 }}
          />
          <button onClick={handleExport} disabled={!currentPatch}>
            Export .maxpat
          </button>
        </div>
        
        <div style={{ marginBottom: 10 }}>
          <button 
            onClick={connectToLive} 
            disabled={isConnected}
            style={{ marginRight: 10, backgroundColor: isConnected ? '#4CAF50' : '#2196F3' }}
          >
            {isConnected ? 'Connected' : 'Connect to Live'}
          </button>
          <span style={{ color: isConnected ? 'green' : 'red', fontSize: 12 }}>
            {isConnected ? '● Connected' : '● Disconnected'}
          </span>
        </div>
        
        {isConnected && (
          <div style={{ marginBottom: 10 }}>
            <label style={{ fontSize: 12 }}>Track: </label>
            <input 
              type="number" 
              value={selectedTrack} 
              onChange={(e) => setSelectedTrack(parseInt(e.target.value))}
              style={{ width: 50, marginRight: 10 }}
            />
            <label style={{ fontSize: 12 }}>Device: </label>
            <input 
              type="number" 
              value={selectedDevice} 
              onChange={(e) => setSelectedDevice(parseInt(e.target.value))}
              style={{ width: 50 }}
            />
          </div>
        )}
        
        {isConnected && currentPatch && (
          <div>
            <button onClick={syncWithLive} style={{ marginRight: 5, fontSize: 12 }}>
              Sync with Live
            </button>
            <button onClick={reloadInLive} style={{ marginRight: 5, fontSize: 12 }}>
              Reload in Live
            </button>
            <button onClick={exportToLive} style={{ fontSize: 12 }}>
              Export to Live
            </button>
          </div>
        )}
      </div>
      
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        onConnect={onConnect}
        nodeTypes={nodeTypes}
      >
        <Controls />
        <MiniMap />
        <Background variant="dots" gap={12} size={1} />
      </ReactFlow>
    </div>
  );
}

export default OriginalApp;
