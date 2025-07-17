import React, { useState, useRef, useEffect } from 'react';
import './MiniMap.css';

const MiniMap = ({
  nodes,
  edges,
  viewport,
  onViewportChange,
  canvasBounds,
  selectedNodes = [],
  onNodeSelect,
  isVisible = true
}) => {
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [size, setSize] = useState({ width: 200, height: 150 });
  const [position, setPosition] = useState({ x: 20, y: 20 });
  
  const miniMapRef = useRef(null);
  const dragRef = useRef(null);
  const resizeRef = useRef(null);

  // Calculate scale to fit all nodes
  const getNodeBounds = () => {
    if (!nodes || nodes.length === 0) {
      return { minX: 0, minY: 0, maxX: 1000, maxY: 1000 };
    }

    let minX = Infinity, minY = Infinity, maxX = -Infinity, maxY = -Infinity;
    
    nodes.forEach(node => {
      minX = Math.min(minX, node.position.x);
      minY = Math.min(minY, node.position.y);
      maxX = Math.max(maxX, node.position.x + (node.width || 150));
      maxY = Math.max(maxY, node.position.y + (node.height || 100));
    });

    // Add padding
    const padding = 100;
    return {
      minX: minX - padding,
      minY: minY - padding,
      maxX: maxX + padding,
      maxY: maxY + padding
    };
  };

  const bounds = getNodeBounds();
  const contentWidth = bounds.maxX - bounds.minX;
  const contentHeight = bounds.maxY - bounds.minY;
  
  const scaleX = size.width / contentWidth;
  const scaleY = size.height / contentHeight;
  const scale = Math.min(scaleX, scaleY);

  // Convert world coordinates to minimap coordinates
  const worldToMiniMap = (worldX, worldY) => {
    return {
      x: (worldX - bounds.minX) * scale,
      y: (worldY - bounds.minY) * scale
    };
  };

  // Convert minimap coordinates to world coordinates
  const miniMapToWorld = (miniX, miniY) => {
    return {
      x: bounds.minX + (miniX / scale),
      y: bounds.minY + (miniY / scale)
    };
  };

  // Calculate viewport rectangle in minimap coordinates
  const getViewportRect = () => {
    const viewportWidth = window.innerWidth / viewport.zoom;
    const viewportHeight = window.innerHeight / viewport.zoom;
    const viewportX = -viewport.x / viewport.zoom;
    const viewportY = -viewport.y / viewport.zoom;

    const topLeft = worldToMiniMap(viewportX, viewportY);
    const bottomRight = worldToMiniMap(
      viewportX + viewportWidth,
      viewportY + viewportHeight
    );

    return {
      x: topLeft.x,
      y: topLeft.y,
      width: bottomRight.x - topLeft.x,
      height: bottomRight.y - topLeft.y
    };
  };

  const viewportRect = getViewportRect();

  // Handle minimap click to pan
  const handleMiniMapClick = (e) => {
    if (isDragging || isResizing) return;

    const rect = miniMapRef.current.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const clickY = e.clientY - rect.top;

    const worldPos = miniMapToWorld(clickX, clickY);
    
    // Center the viewport on the clicked position
    const newViewport = {
      x: -worldPos.x * viewport.zoom + window.innerWidth / 2,
      y: -worldPos.y * viewport.zoom + window.innerHeight / 2,
      zoom: viewport.zoom
    };

    onViewportChange(newViewport);
  };

  // Handle viewport drag
  const handleViewportDrag = (e) => {
    if (!isDragging) return;

    const rect = miniMapRef.current.getBoundingClientRect();
    const dragX = e.clientX - rect.left - dragRef.current.offsetX;
    const dragY = e.clientY - rect.top - dragRef.current.offsetY;

    const worldPos = miniMapToWorld(dragX, dragY);
    
    const newViewport = {
      x: -worldPos.x * viewport.zoom,
      y: -worldPos.y * viewport.zoom,
      zoom: viewport.zoom
    };

    onViewportChange(newViewport);
  };

  // Handle resize drag
  const handleResize = (e) => {
    if (!isResizing) return;

    const deltaX = e.clientX - resizeRef.current.startX;
    const deltaY = e.clientY - resizeRef.current.startY;

    const newWidth = Math.max(100, resizeRef.current.startWidth + deltaX);
    const newHeight = Math.max(75, resizeRef.current.startHeight + deltaY);

    setSize({ width: newWidth, height: newHeight });
  };

  // Mouse event handlers
  useEffect(() => {
    const handleMouseMove = (e) => {
      handleViewportDrag(e);
      handleResize(e);
    };

    const handleMouseUp = () => {
      setIsDragging(false);
      setIsResizing(false);
      dragRef.current = null;
      resizeRef.current = null;
    };

    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);

      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isResizing]);

  const startViewportDrag = (e) => {
    const rect = miniMapRef.current.getBoundingClientRect();
    const offsetX = e.clientX - rect.left - viewportRect.x;
    const offsetY = e.clientY - rect.top - viewportRect.y;

    setIsDragging(true);
    dragRef.current = { offsetX, offsetY };
  };

  const startResize = (e) => {
    e.stopPropagation();
    setIsResizing(true);
    resizeRef.current = {
      startX: e.clientX,
      startY: e.clientY,
      startWidth: size.width,
      startHeight: size.height
    };
  };

  const getNodeColor = (node) => {
    if (selectedNodes.includes(node.id)) return '#007acc';
    
    switch (node.data.status) {
      case 'connected': return '#10b981';
      case 'running': return '#f59e0b';
      case 'error': return '#ef4444';
      case 'disabled': return '#6b7280';
      default: return '#9ca3af';
    }
  };

  const getEdgeColor = (edge) => {
    const sourceNode = nodes.find(n => n.id === edge.source);
    const targetNode = nodes.find(n => n.id === edge.target);
    
    if (sourceNode?.data.status === 'error' || targetNode?.data.status === 'error') {
      return '#ef4444';
    }
    
    if (sourceNode?.data.status === 'connected' && targetNode?.data.status === 'connected') {
      return '#10b981';
    }
    
    return '#4b5563';
  };

  if (!isVisible) return null;

  return (
    <div 
      className="minimap-container"
      style={{
        left: position.x,
        top: position.y,
        width: size.width + 20,
        height: size.height + 40
      }}
    >
      {/* Header */}
      <div className="minimap-header">
        <span className="minimap-title">Mini-Map</span>
        <div className="minimap-controls">
          <button
            className="minimap-control-btn"
            onClick={() => {
              // Fit all nodes
              const newViewport = {
                x: -bounds.minX * 0.5 + 50,
                y: -bounds.minY * 0.5 + 50,
                zoom: 0.5
              };
              onViewportChange(newViewport);
            }}
            title="Fit All"
          >
            📐
          </button>
          <button
            className="minimap-control-btn"
            onClick={() => {
              // Reset zoom
              onViewportChange({ x: 0, y: 0, zoom: 1 });
            }}
            title="Reset View"
          >
            🎯
          </button>
        </div>
      </div>

      {/* MiniMap Canvas */}
      <div
        ref={miniMapRef}
        className="minimap-canvas"
        style={{ width: size.width, height: size.height }}
        onClick={handleMiniMapClick}
      >
        {/* Background Grid */}
        <div className="minimap-grid" />

        {/* Edges */}
        <svg 
          className="minimap-edges"
          width={size.width}
          height={size.height}
        >
          {edges.map(edge => {
            const sourceNode = nodes.find(n => n.id === edge.source);
            const targetNode = nodes.find(n => n.id === edge.target);
            
            if (!sourceNode || !targetNode) return null;

            const sourcePos = worldToMiniMap(
              sourceNode.position.x + (sourceNode.width || 150) / 2,
              sourceNode.position.y + (sourceNode.height || 100) / 2
            );
            const targetPos = worldToMiniMap(
              targetNode.position.x + (targetNode.width || 150) / 2,
              targetNode.position.y + (targetNode.height || 100) / 2
            );

            return (
              <line
                key={edge.id}
                x1={sourcePos.x}
                y1={sourcePos.y}
                x2={targetPos.x}
                y2={targetPos.y}
                stroke={getEdgeColor(edge)}
                strokeWidth={1}
                opacity={0.6}
              />
            );
          })}
        </svg>

        {/* Nodes */}
        {nodes.map(node => {
          const pos = worldToMiniMap(node.position.x, node.position.y);
          const nodeWidth = (node.width || 150) * scale;
          const nodeHeight = (node.height || 100) * scale;

          return (
            <div
              key={node.id}
              className="minimap-node"
              style={{
                left: pos.x,
                top: pos.y,
                width: Math.max(3, nodeWidth),
                height: Math.max(2, nodeHeight),
                backgroundColor: getNodeColor(node),
                borderRadius: scale > 0.02 ? '2px' : '1px'
              }}
              onClick={(e) => {
                e.stopPropagation();
                onNodeSelect?.(node.id);
              }}
              title={node.data.label}
            />
          );
        })}

        {/* Viewport Rectangle */}
        <div
          className="minimap-viewport"
          style={{
            left: Math.max(0, viewportRect.x),
            top: Math.max(0, viewportRect.y),
            width: Math.min(size.width - Math.max(0, viewportRect.x), viewportRect.width),
            height: Math.min(size.height - Math.max(0, viewportRect.y), viewportRect.height)
          }}
          onMouseDown={startViewportDrag}
        />

        {/* Zoom Level Indicator */}
        <div className="minimap-zoom-indicator">
          {Math.round(viewport.zoom * 100)}%
        </div>
      </div>

      {/* Statistics */}
      <div className="minimap-stats">
        <span className="stat-item">
          <span className="stat-label">Nodes:</span>
          <span className="stat-value">{nodes.length}</span>
        </span>
        <span className="stat-item">
          <span className="stat-label">Edges:</span>
          <span className="stat-value">{edges.length}</span>
        </span>
      </div>

      {/* Resize Handle */}
      <div
        className="minimap-resize-handle"
        onMouseDown={startResize}
      />
    </div>
  );
};

export default MiniMap;
