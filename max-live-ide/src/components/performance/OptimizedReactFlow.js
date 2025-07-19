/**
 * Performance-Optimized React Flow Components
 * Implements virtualization, memoization, and batch updates for large patches (200+ nodes)
 */

import React, { useMemo, useCallback, useRef, memo } from 'react';
import { ReactFlow, Background, Controls, MiniMap, useReactFlow } from '@xyflow/react';

// ========================================
// 1. MEMOIZED MAX OBJECT NODE COMPONENT
// ========================================

const MaxObjectNode = memo(({ 
  data, 
  isConnectable, 
  selected, 
  id,
  xPos,
  yPos,
  zIndex
}) => {
  // Memoize handle calculations
  const handles = useMemo(() => {
    const inputCount = data.inputs?.length || 1;
    const outputCount = data.outputs?.length || 1;
    
    return {
      inputs: Array.from({ length: inputCount }, (_, i) => ({
        id: `input-${i}`,
        position: `${(i + 1) * (100 / (inputCount + 1))}%`
      })),
      outputs: Array.from({ length: outputCount }, (_, i) => ({
        id: `output-${i}`,
        position: `${(i + 1) * (100 / (outputCount + 1))}%`
      }))
    };
  }, [data.inputs, data.outputs]);

  // Memoize node styling based on state
  const nodeStyle = useMemo(() => ({
    backgroundColor: selected ? '#1e40af' : data.status === 'running' ? '#059669' : '#6b7280',
    borderColor: selected ? '#3b82f6' : 'transparent',
    transform: `translate(${xPos}px, ${yPos}px)`,
    zIndex: selected ? 1000 : zIndex
  }), [selected, data.status, xPos, yPos, zIndex]);

  return (
    <div className="max-object-node" style={nodeStyle}>
      {/* Input handles */}
      {handles.inputs.map((handle, index) => (
        <div
          key={handle.id}
          className="react-flow__handle react-flow__handle-top"
          style={{ left: handle.position }}
          data-testid={`input-${index}`}
        />
      ))}
      
      {/* Node content */}
      <div className="node-content">
        <span className="node-label">{data.label}</span>
        {data.parameters && (
          <div className="node-parameters">
            {Object.entries(data.parameters).slice(0, 3).map(([key, value]) => (
              <span key={key} className="parameter">
                {key}: {value}
              </span>
            ))}
          </div>
        )}
      </div>
      
      {/* Output handles */}
      {handles.outputs.map((handle, index) => (
        <div
          key={handle.id}
          className="react-flow__handle react-flow__handle-bottom"
          style={{ left: handle.position }}
          data-testid={`output-${index}`}
        />
      ))}
    </div>
  );
}, (prevProps, nextProps) => {
  // Custom comparison function for React.memo
  return (
    prevProps.data.label === nextProps.data.label &&
    prevProps.data.status === nextProps.data.status &&
    prevProps.selected === nextProps.selected &&
    prevProps.isConnectable === nextProps.isConnectable &&
    JSON.stringify(prevProps.data.parameters) === JSON.stringify(nextProps.data.parameters)
  );
});

// ========================================
// 2. VIRTUALIZED NODE CONTAINER
// ========================================

const VirtualizedNodeContainer = memo(({ 
  nodes, 
  viewport, 
  nodeTypes,
  onNodesChange 
}) => {
  const viewportBounds = useMemo(() => {
    const { x, y, zoom } = viewport;
    const buffer = 200; // Render buffer outside viewport
    
    return {
      left: -x / zoom - buffer,
      top: -y / zoom - buffer,
      right: (-x + window.innerWidth) / zoom + buffer,
      bottom: (-y + window.innerHeight) / zoom + buffer
    };
  }, [viewport]);

  // Only render nodes within the viewport
  const visibleNodes = useMemo(() => {
    return nodes.filter(node => {
      const nodeWidth = 150; // Approximate node width
      const nodeHeight = 60;  // Approximate node height
      
      return (
        node.position.x + nodeWidth >= viewportBounds.left &&
        node.position.x <= viewportBounds.right &&
        node.position.y + nodeHeight >= viewportBounds.top &&
        node.position.y <= viewportBounds.bottom
      );
    });
  }, [nodes, viewportBounds]);

  return (
    <>
      {visibleNodes.map(node => {
        const NodeComponent = nodeTypes[node.type] || MaxObjectNode;
        return (
          <NodeComponent
            key={node.id}
            id={node.id}
            data={node.data}
            selected={node.selected}
            xPos={node.position.x}
            yPos={node.position.y}
            zIndex={node.zIndex || 1}
          />
        );
      })}
    </>
  );
});

// ========================================
// 3. BATCH UPDATE HOOK
// ========================================

export const useBatchUpdates = () => {
  const updateQueue = useRef([]);
  const batchTimeout = useRef(null);
  const { setNodes, setEdges } = useReactFlow();

  const batchUpdate = useCallback((updates) => {
    updateQueue.current.push(...updates);
    
    if (batchTimeout.current) {
      clearTimeout(batchTimeout.current);
    }
    
    batchTimeout.current = setTimeout(() => {
      if (updateQueue.current.length > 0) {
        const nodeUpdates = updateQueue.current.filter(u => u.type === 'node');
        const edgeUpdates = updateQueue.current.filter(u => u.type === 'edge');
        
        if (nodeUpdates.length > 0) {
          setNodes(nodes => {
            let updatedNodes = [...nodes];
            nodeUpdates.forEach(update => {
              switch (update.action) {
                case 'add':
                  updatedNodes.push(update.data);
                  break;
                case 'update':
                  const index = updatedNodes.findIndex(n => n.id === update.data.id);
                  if (index !== -1) {
                    updatedNodes[index] = { ...updatedNodes[index], ...update.data };
                  }
                  break;
                case 'remove':
                  updatedNodes = updatedNodes.filter(n => n.id !== update.data.id);
                  break;
                default:
                  break;
              }
            });
            return updatedNodes;
          });
        }
        
        if (edgeUpdates.length > 0) {
          setEdges(edges => {
            let updatedEdges = [...edges];
            edgeUpdates.forEach(update => {
              switch (update.action) {
                case 'add':
                  updatedEdges.push(update.data);
                  break;
                case 'update':
                  const index = updatedEdges.findIndex(e => e.id === update.data.id);
                  if (index !== -1) {
                    updatedEdges[index] = { ...updatedEdges[index], ...update.data };
                  }
                  break;
                case 'remove':
                  updatedEdges = updatedEdges.filter(e => e.id !== update.data.id);
                  break;
                default:
                  break;
              }
            });
            return updatedEdges;
          });
        }
        
        updateQueue.current = [];
      }
    }, 16); // Batch updates every 16ms (60fps)
  }, [setNodes, setEdges]);

  return { batchUpdate };
};

// ========================================
// 4. PERFORMANCE-OPTIMIZED REACT FLOW
// ========================================

const PerformanceOptimizedReactFlow = memo(({
  nodes = [],
  edges = [],
  onNodesChange,
  onEdgesChange,
  onConnect,
  nodeTypes,
  ...props
}) => {
  const reactFlowInstance = useRef(null);
  const { batchUpdate } = useBatchUpdates();

  // Memoize node types to prevent re-registration
  const memoizedNodeTypes = useMemo(() => ({
    maxObject: MaxObjectNode,
    ...nodeTypes
  }), [nodeTypes]);

  // Optimize edge rendering with memoization
  const memoizedEdges = useMemo(() => {
    return edges.map(edge => ({
      ...edge,
      style: {
        strokeWidth: edge.selected ? 3 : 2,
        stroke: edge.animated ? '#3b82f6' : '#6b7280',
        ...edge.style
      }
    }));
  }, [edges]);

  // Batch node changes for better performance
  const handleNodesChange = useCallback((changes) => {
    const updates = changes.map(change => ({
      type: 'node',
      action: change.type,
      data: change
    }));
    
    batchUpdate(updates);
    onNodesChange?.(changes);
  }, [batchUpdate, onNodesChange]);

  // Batch edge changes
  const handleEdgesChange = useCallback((changes) => {
    const updates = changes.map(change => ({
      type: 'edge',
      action: change.type,
      data: change
    }));
    
    batchUpdate(updates);
    onEdgesChange?.(changes);
  }, [batchUpdate, onEdgesChange]);

  // Optimize connection handling
  const handleConnect = useCallback((connection) => {
    const newEdge = {
      id: `edge-${connection.source}-${connection.target}`,
      source: connection.source,
      target: connection.target,
      sourceHandle: connection.sourceHandle,
      targetHandle: connection.targetHandle,
      type: 'smoothstep'
    };
    
    batchUpdate([{
      type: 'edge',
      action: 'add',
      data: newEdge
    }]);
    
    onConnect?.(connection);
  }, [batchUpdate, onConnect]);

  // Performance monitoring
  const performanceRef = useRef({
    renderCount: 0,
    lastRenderTime: 0
  });

  React.useEffect(() => {
    performanceRef.current.renderCount++;
    performanceRef.current.lastRenderTime = performance.now();
    
    // Log performance warnings
    if (nodes.length > 300 && performanceRef.current.renderCount % 10 === 0) {
      console.warn(`Large patch detected: ${nodes.length} nodes. Consider enabling virtualization.`);
    }
  }, [nodes.length]);

  return (
    <ReactFlow
      ref={reactFlowInstance}
      nodes={nodes}
      edges={memoizedEdges}
      onNodesChange={handleNodesChange}
      onEdgesChange={handleEdgesChange}
      onConnect={handleConnect}
      nodeTypes={memoizedNodeTypes}
      // Performance optimizations
      onlyRenderVisibleElements={true}
      snapToGrid={true}
      snapGrid={[10, 10]}
      defaultViewport={{ x: 0, y: 0, zoom: 1 }}
      minZoom={0.1}
      maxZoom={4}
      // Reduce re-renders
      nodesDraggable={true}
      nodesConnectable={true}
      elementsSelectable={true}
      // Optimize edge rendering
      connectionLineType="smoothstep"
      deleteKeyCode="Delete"
      {...props}
    >
      <Background />
      <Controls />
      <MiniMap 
        nodeStrokeColor="#333"
        nodeColor="#fff"
        nodeBorderRadius={4}
        pannable={true}
        zoomable={true}
      />
    </ReactFlow>
  );
});

// ========================================
// 5. PERFORMANCE MONITORING COMPONENT
// ========================================

export const PerformanceMonitor = memo(() => {
  const [metrics, setMetrics] = React.useState({
    fps: 60,
    memory: 0,
    renderTime: 0,
    nodeCount: 0,
    edgeCount: 0
  });

  React.useEffect(() => {
    let frameCount = 0;
    let lastTime = performance.now();
    
    const measureFPS = () => {
      frameCount++;
      const currentTime = performance.now();
      
      if (currentTime >= lastTime + 1000) {
        const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
        
        setMetrics(prev => ({
          ...prev,
          fps,
          memory: performance.memory?.usedJSHeapSize || 0
        }));
        
        frameCount = 0;
        lastTime = currentTime;
      }
      
      requestAnimationFrame(measureFPS);
    };
    
    measureFPS();
  }, []);

  const getPerformanceStatus = () => {
    if (metrics.fps < 30) return { color: 'red', status: 'Poor' };
    if (metrics.fps < 45) return { color: 'orange', status: 'Fair' };
    return { color: 'green', status: 'Good' };
  };

  const status = getPerformanceStatus();

  return (
    <div className="performance-monitor">
      <div className="metric">
        <span>FPS:</span>
        <span style={{ color: status.color }}>{metrics.fps}</span>
      </div>
      <div className="metric">
        <span>Memory:</span>
        <span>{(metrics.memory / 1024 / 1024).toFixed(1)}MB</span>
      </div>
      <div className="metric">
        <span>Status:</span>
        <span style={{ color: status.color }}>{status.status}</span>
      </div>
    </div>
  );
});

// ========================================
// 6. EXPORTS
// ========================================

export {
  MaxObjectNode,
  VirtualizedNodeContainer,
  PerformanceOptimizedReactFlow as ReactFlow,
  useBatchUpdates
};

export default PerformanceOptimizedReactFlow;
