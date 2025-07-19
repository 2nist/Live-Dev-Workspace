import React, { useState, useEffect, useMemo, useRef, useCallback } from 'react';
import './DeviceManager.css';

const DeviceManager = ({
  nodes,
  onNodeUpdate,
  onStatusUpdate,
  onClose,
  deviceStatuses,
  scriptStatuses
}) => {
  const [searchTerm, setSearchTerm] = useState('');
  const [filterType, setFilterType] = useState('all');
  const [filterStatus, setFilterStatus] = useState('all');
  const [selectedTags, setSelectedTags] = useState([]);
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Window state for floating behavior
  const [windowPosition, setWindowPosition] = useState({ x: 100, y: 100 });
  const [windowSize, setWindowSize] = useState({ width: 500, height: 600 });
  const [isDragging, setIsDragging] = useState(false);
  const [isResizing, setIsResizing] = useState(false);
  const [dragStart, setDragStart] = useState({ x: 0, y: 0 });
  const [resizeStart, setResizeStart] = useState({ x: 0, y: 0, width: 0, height: 0 });
  const [isMinimized, setIsMinimized] = useState(false);
  
  const windowRef = useRef(null);
  const headerRef = useRef(null);

  // Extract all unique tags from nodes
  const allTags = useMemo(() => {
    const tagSet = new Set();
    nodes.forEach(node => {
      if (node.data.tags) {
        node.data.tags.forEach(tag => tagSet.add(tag));
      }
    });
    return Array.from(tagSet).sort();
  }, [nodes]);

  // Filter and sort nodes
  const filteredAndSortedNodes = useMemo(() => {
    let filtered = nodes.filter(node => {
      // Search term filter
      const matchesSearch = !searchTerm || 
        node.data.label.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (node.data.tags && node.data.tags.some(tag => 
          tag.toLowerCase().includes(searchTerm.toLowerCase())
        ));

      // Type filter
      const matchesType = filterType === 'all' || 
        node.data.objectType === filterType;

      // Status filter
      const matchesStatus = filterStatus === 'all' || 
        node.data.status === filterStatus;

      // Tags filter
      const matchesTags = selectedTags.length === 0 || 
        (node.data.tags && selectedTags.every(tag => 
          node.data.tags.includes(tag)
        ));

      return matchesSearch && matchesType && matchesStatus && matchesTags;
    });

    // Sort nodes
    filtered.sort((a, b) => {
      let comparison = 0;
      
      switch (sortBy) {
        case 'name':
          comparison = a.data.label.localeCompare(b.data.label);
          break;
        case 'type':
          comparison = (a.data.objectType || '').localeCompare(b.data.objectType || '');
          break;
        case 'status':
          comparison = (a.data.status || '').localeCompare(b.data.status || '');
          break;
        default:
          comparison = 0;
      }
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

    return filtered;
  }, [nodes, searchTerm, filterType, filterStatus, selectedTags, sortBy, sortOrder]);

  // Status statistics
  const statusStats = useMemo(() => {
    const stats = {
      connected: 0,
      running: 0,
      error: 0,
      disabled: 0,
      total: nodes.length
    };
    
    nodes.forEach(node => {
      const status = node.data.status || 'disabled';
      if (stats.hasOwnProperty(status)) {
        stats[status]++;
      }
    });
    
    return stats;
  }, [nodes]);

  // Window drag handlers
  const handleMouseDown = useCallback((e) => {
    if (e.target === headerRef.current || headerRef.current?.contains(e.target)) {
      setIsDragging(true);
      setDragStart({
        x: e.clientX - windowPosition.x,
        y: e.clientY - windowPosition.y
      });
    }
  }, [windowPosition]);

  const handleMouseMove = useCallback((e) => {
    if (isDragging) {
      setWindowPosition({
        x: e.clientX - dragStart.x,
        y: e.clientY - dragStart.y
      });
    } else if (isResizing) {
      const newWidth = Math.max(300, resizeStart.width + (e.clientX - resizeStart.x));
      const newHeight = Math.max(200, resizeStart.height + (e.clientY - resizeStart.y));
      setWindowSize({ width: newWidth, height: newHeight });
    }
  }, [isDragging, isResizing, dragStart, resizeStart]);

  const handleMouseUp = useCallback(() => {
    setIsDragging(false);
    setIsResizing(false);
  }, []);

  const handleResizeStart = useCallback((e) => {
    e.stopPropagation();
    setIsResizing(true);
    setResizeStart({
      x: e.clientX,
      y: e.clientY,
      width: windowSize.width,
      height: windowSize.height
    });
  }, [windowSize]);

  // Window control handlers
  const handleMinimize = () => {
    setIsMinimized(!isMinimized);
  };

  const handleMaximize = () => {
    if (windowSize.width === window.innerWidth && windowSize.height === window.innerHeight) {
      setWindowSize({ width: 500, height: 600 });
      setWindowPosition({ x: 100, y: 100 });
    } else {
      setWindowSize({ width: window.innerWidth, height: window.innerHeight });
      setWindowPosition({ x: 0, y: 0 });
    }
  };

  // Global mouse event listeners
  useEffect(() => {
    if (isDragging || isResizing) {
      document.addEventListener('mousemove', handleMouseMove);
      document.addEventListener('mouseup', handleMouseUp);
      return () => {
        document.removeEventListener('mousemove', handleMouseMove);
        document.removeEventListener('mouseup', handleMouseUp);
      };
    }
  }, [isDragging, isResizing, handleMouseMove, handleMouseUp]);

  const handleTagToggle = (tag) => {
    setSelectedTags(prev => 
      prev.includes(tag) 
        ? prev.filter(t => t !== tag)
        : [...prev, tag]
    );
  };

  const handleStatusChange = (nodeId, newStatus) => {
    onStatusUpdate(nodeId, newStatus);
    onNodeUpdate(nodes => nodes.map(node => 
      node.id === nodeId 
        ? { ...node, data: { ...node.data, status: newStatus } }
        : node
    ));
  };

  const getStatusIcon = (status) => {
    switch (status) {
      case 'connected': return '🟢';
      case 'running': return '🟡';
      case 'error': return '🔴';
      case 'disabled': return '⚫';
      default: return '⚪';
    }
  };

  const getTypeIcon = (type) => {
    switch (type) {
      case 'audio': return '🎵';
      case 'midi': return '🎹';
      case 'live-api': return '🎛️';
      case 'utility': return '🔧';
      default: return '📦';
    }
  };

  // Action handlers for individual devices
  const handleEditDevice = (nodeId) => {
    console.log('Edit device:', nodeId);
    // TODO: Open device editor/inspector
    alert(`Edit device: ${nodeId}`);
  };

  const handleTestDevice = (nodeId) => {
    console.log('Test device:', nodeId);
    // TODO: Run device test
    onStatusUpdate(nodeId, 'running');
    setTimeout(() => {
      onStatusUpdate(nodeId, 'connected');
    }, 2000);
    alert(`Testing device: ${nodeId}`);
  };

  const handleResetDevice = (nodeId) => {
    console.log('Reset device:', nodeId);
    // TODO: Reset device state
    onStatusUpdate(nodeId, 'disabled');
    setTimeout(() => {
      onStatusUpdate(nodeId, 'connected');
    }, 1000);
    alert(`Reset device: ${nodeId}`);
  };

  const handleRemoveDevice = (nodeId) => {
    console.log('Remove device:', nodeId);
    // TODO: Remove device from patch
    if (window.confirm('Are you sure you want to remove this device?')) {
      onNodeUpdate(nodes => nodes.filter(node => node.id !== nodeId));
      alert(`Removed device: ${nodeId}`);
    }
  };

  // Bulk action handlers
  const handleBulkEnable = () => {
    console.log('Enable all devices');
    filteredAndSortedNodes.forEach(node => {
      onStatusUpdate(node.id, 'connected');
    });
    alert(`Enabled ${filteredAndSortedNodes.length} devices`);
  };

  const handleBulkDisable = () => {
    console.log('Disable all devices');
    filteredAndSortedNodes.forEach(node => {
      onStatusUpdate(node.id, 'disabled');
    });
    alert(`Disabled ${filteredAndSortedNodes.length} devices`);
  };

  const handleBulkTest = () => {
    console.log('Test all devices');
    filteredAndSortedNodes.forEach((node, index) => {
      setTimeout(() => {
        onStatusUpdate(node.id, 'running');
        setTimeout(() => {
          onStatusUpdate(node.id, 'connected');
        }, 1000);
      }, index * 200);
    });
    alert(`Testing ${filteredAndSortedNodes.length} devices`);
  };

  const handleBulkReset = () => {
    console.log('Reset all devices');
    if (window.confirm(`Are you sure you want to reset all ${filteredAndSortedNodes.length} devices?`)) {
      filteredAndSortedNodes.forEach((node, index) => {
        setTimeout(() => {
          onStatusUpdate(node.id, 'disabled');
          setTimeout(() => {
            onStatusUpdate(node.id, 'connected');
          }, 500);
        }, index * 100);
      });
      alert(`Reset ${filteredAndSortedNodes.length} devices`);
    }
  };

  return (
    <div 
      ref={windowRef}
      className={`floating-device-manager ${isMinimized ? 'minimized' : ''}`}
      style={{
        position: 'fixed',
        left: windowPosition.x,
        top: windowPosition.y,
        width: windowSize.width,
        height: isMinimized ? 'auto' : windowSize.height,
        zIndex: 1000,
        border: '1px solid #444',
        borderRadius: '8px',
        backgroundColor: '#2a2a2a',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.3)',
        display: 'flex',
        flexDirection: 'column',
        overflow: 'hidden'
      }}
      onMouseDown={handleMouseDown}
    >
      {/* Window Header with Drag Handle */}
      <div 
        ref={headerRef}
        className="floating-window-header"
        style={{
          background: 'linear-gradient(90deg, #333, #2a2a2a)',
          borderBottom: '1px solid #444',
          padding: '8px 16px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          cursor: isDragging ? 'grabbing' : 'grab',
          userSelect: 'none'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <span style={{ color: '#007acc', fontSize: '16px' }}>⚙️</span>
          <h2 style={{ color: '#007acc', fontSize: '14px', fontWeight: '600', margin: 0 }}>
            Device & Script Manager
          </h2>
          <span style={{ 
            background: '#007acc', 
            color: 'white', 
            padding: '2px 8px', 
            borderRadius: '12px', 
            fontSize: '11px',
            fontWeight: 'bold'
          }}>
            {statusStats.total}
          </span>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
          <button 
            className="window-control-button"
            onClick={handleMinimize}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#ccc',
              padding: '4px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
            title={isMinimized ? 'Restore' : 'Minimize'}
          >
            {isMinimized ? '🔲' : '➖'}
          </button>
          <button 
            className="window-control-button"
            onClick={handleMaximize}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#ccc',
              padding: '4px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
            title="Maximize/Restore"
          >
            🔳
          </button>
          <button 
            className="window-control-button"
            onClick={onClose}
            style={{
              background: 'transparent',
              border: 'none',
              color: '#ff6b6b',
              padding: '4px 8px',
              borderRadius: '4px',
              cursor: 'pointer',
              fontSize: '12px'
            }}
            title="Close"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Window Content */}
      {!isMinimized && (
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>
          {/* Statistics Bar */}
          <div className="status-statistics" style={{
            display: 'flex',
            gap: '12px',
            padding: '8px 16px',
            background: '#333',
            borderBottom: '1px solid #444',
            fontSize: '11px'
          }}>
            <div className="stat-item">
              <span className="stat-icon">📊</span>
              <span className="stat-label">Total: {statusStats.total}</span>
            </div>
            <div className="stat-item connected">
              <span className="stat-icon">🟢</span>
              <span className="stat-label">Connected: {statusStats.connected}</span>
            </div>
            <div className="stat-item running">
              <span className="stat-icon">🟡</span>
              <span className="stat-label">Running: {statusStats.running}</span>
            </div>
            <div className="stat-item error">
              <span className="stat-icon">🔴</span>
              <span className="stat-label">Error: {statusStats.error}</span>
            </div>
            <div className="stat-item disabled">
              <span className="stat-icon">⚫</span>
              <span className="stat-label">Disabled: {statusStats.disabled}</span>
            </div>
          </div>

          {/* Search and Filters */}
          <div className="device-manager-controls" style={{
            padding: '12px 16px',
            borderBottom: '1px solid #444',
            background: '#2a2a2a'
          }}>
            <div className="search-section" style={{ marginBottom: '8px' }}>
              <input
                type="text"
                placeholder="Search devices and scripts..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="search-input"
                style={{
                  width: '100%',
                  padding: '6px 12px',
                  background: '#333',
                  border: '1px solid #444',
                  borderRadius: '4px',
                  color: '#fff',
                  fontSize: '12px'
                }}
              />
            </div>

            <div className="filter-section" style={{
              display: 'flex',
              gap: '8px',
              flexWrap: 'wrap',
              marginBottom: '8px'
            }}>
              <select
                value={filterType}
                onChange={(e) => setFilterType(e.target.value)}
                className="filter-select"
                style={{
                  padding: '4px 8px',
                  background: '#333',
                  border: '1px solid #444',
                  borderRadius: '4px',
                  color: '#fff',
                  fontSize: '11px'
                }}
              >
                <option value="all">All Types</option>
                <option value="audio">Audio</option>
                <option value="midi">MIDI</option>
                <option value="live-api">Live API</option>
                <option value="utility">Utility</option>
              </select>

              <select
                value={filterStatus}
                onChange={(e) => setFilterStatus(e.target.value)}
                className="filter-select"
                style={{
                  padding: '4px 8px',
                  background: '#333',
                  border: '1px solid #444',
                  borderRadius: '4px',
                  color: '#fff',
                  fontSize: '11px'
                }}
              >
                <option value="all">All Status</option>
                <option value="connected">Connected</option>
                <option value="running">Running</option>
                <option value="error">Error</option>
                <option value="disabled">Disabled</option>
              </select>

              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value)}
                className="filter-select"
                style={{
                  padding: '4px 8px',
                  background: '#333',
                  border: '1px solid #444',
                  borderRadius: '4px',
                  color: '#fff',
                  fontSize: '11px'
                }}
              >
                <option value="name">Sort by Name</option>
                <option value="type">Sort by Type</option>
                <option value="status">Sort by Status</option>
              </select>

              <button
                className="sort-order-button"
                onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
                title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
                style={{
                  padding: '4px 8px',
                  background: '#333',
                  border: '1px solid #444',
                  borderRadius: '4px',
                  color: '#fff',
                  cursor: 'pointer',
                  fontSize: '11px'
                }}
              >
                {sortOrder === 'asc' ? '↑' : '↓'}
              </button>
            </div>

            {/* Tag Filter */}
            {allTags.length > 0 && (
              <div className="tag-section">
                <div className="tag-label" style={{ color: '#999', fontSize: '11px', marginBottom: '4px' }}>
                  Filter by Tags:
                </div>
                <div className="tag-list" style={{ display: 'flex', gap: '4px', flexWrap: 'wrap' }}>
                  {allTags.map(tag => (
                    <button
                      key={tag}
                      className={`tag-button ${selectedTags.includes(tag) ? 'selected' : ''}`}
                      onClick={() => handleTagToggle(tag)}
                      style={{
                        padding: '2px 6px',
                        background: selectedTags.includes(tag) ? '#007acc' : '#444',
                        border: 'none',
                        borderRadius: '12px',
                        color: '#fff',
                        fontSize: '10px',
                        cursor: 'pointer'
                      }}
                    >
                      {tag}
                    </button>
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Device List */}
          <div className="device-list" style={{
            flex: 1,
            overflow: 'auto',
            padding: '8px 16px'
          }}>
            <div className="list-header" style={{
              display: 'grid',
              gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
              gap: '8px',
              padding: '8px 0',
              borderBottom: '1px solid #444',
              color: '#999',
              fontSize: '11px',
              fontWeight: 'bold'
            }}>
              <span className="column-header name">Name</span>
              <span className="column-header type">Type</span>
              <span className="column-header status">Status</span>
              <span className="column-header tags">Tags</span>
              <span className="column-header actions">Actions</span>
            </div>

            <div className="list-content">
              {filteredAndSortedNodes.map(node => (
                <div key={node.id} className="device-item" style={{
                  display: 'grid',
                  gridTemplateColumns: '2fr 1fr 1fr 1fr 1fr',
                  gap: '8px',
                  padding: '8px 0',
                  borderBottom: '1px solid #333',
                  alignItems: 'center',
                  fontSize: '12px'
                }}>
                  <div className="device-name" style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <span className="type-icon">{getTypeIcon(node.data.objectType)}</span>
                    <span className="name-text" style={{ color: '#fff' }}>{node.data.label}</span>
                  </div>
                  
                  <div className="device-type" style={{ color: '#999' }}>
                    {node.data.objectType || 'unknown'}
                  </div>
                  
                  <div className="device-status" style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                    <span className="status-icon">{getStatusIcon(node.data.status)}</span>
                    <select
                      value={node.data.status || 'disabled'}
                      onChange={(e) => handleStatusChange(node.id, e.target.value)}
                      className="status-select"
                      style={{
                        padding: '2px 4px',
                        background: '#333',
                        border: '1px solid #444',
                        borderRadius: '3px',
                        color: '#fff',
                        fontSize: '10px'
                      }}
                    >
                      <option value="connected">Connected</option>
                      <option value="running">Running</option>
                      <option value="error">Error</option>
                      <option value="disabled">Disabled</option>
                    </select>
                  </div>
                  
                  <div className="device-tags" style={{ display: 'flex', gap: '2px', flexWrap: 'wrap' }}>
                    {node.data.tags && node.data.tags.map(tag => (
                      <span key={tag} className="tag" style={{
                        background: '#444',
                        color: '#ccc',
                        padding: '1px 4px',
                        borderRadius: '8px',
                        fontSize: '9px'
                      }}>
                        {tag}
                      </span>
                    ))}
                  </div>
                  
                  <div className="device-actions" style={{ display: 'flex', gap: '4px' }}>
                    <button 
                      className="action-button" 
                      title="Edit" 
                      onClick={() => handleEditDevice(node.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#ccc',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}>✏️</button>
                    <button 
                      className="action-button" 
                      title="Test" 
                      onClick={() => handleTestDevice(node.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#ccc',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}>🧪</button>
                    <button 
                      className="action-button" 
                      title="Reset" 
                      onClick={() => handleResetDevice(node.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#ccc',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}>🔄</button>
                    <button 
                      className="action-button danger" 
                      title="Remove" 
                      onClick={() => handleRemoveDevice(node.id)}
                      style={{
                        background: 'transparent',
                        border: 'none',
                        color: '#ff6b6b',
                        cursor: 'pointer',
                        fontSize: '11px'
                      }}>🗑️</button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Bulk Actions */}
          <div className="bulk-actions" style={{
            display: 'flex',
            gap: '8px',
            padding: '12px 16px',
            borderTop: '1px solid #444',
            background: '#333'
          }}>
            <button 
              className="bulk-button" 
              onClick={handleBulkEnable}
              style={{
                padding: '6px 12px',
                background: '#444',
                border: '1px solid #555',
                borderRadius: '4px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '11px'
              }}>Enable All</button>
            <button 
              className="bulk-button" 
              onClick={handleBulkDisable}
              style={{
                padding: '6px 12px',
                background: '#444',
                border: '1px solid #555',
                borderRadius: '4px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '11px'
              }}>Disable All</button>
            <button 
              className="bulk-button" 
              onClick={handleBulkTest}
              style={{
                padding: '6px 12px',
                background: '#444',
                border: '1px solid #555',
                borderRadius: '4px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '11px'
              }}>Test All</button>
            <button 
              className="bulk-button" 
              onClick={handleBulkReset}
              style={{
                padding: '6px 12px',
                background: '#444',
                border: '1px solid #555',
                borderRadius: '4px',
                color: '#fff',
                cursor: 'pointer',
                fontSize: '11px'
              }}>Reset All</button>
          </div>
        </div>
      )}

      {/* Resize Handle */}
      {!isMinimized && (
        <div
          className="resize-handle"
          onMouseDown={handleResizeStart}
          style={{
            position: 'absolute',
            bottom: 0,
            right: 0,
            width: '20px',
            height: '20px',
            cursor: 'nw-resize',
            background: 'linear-gradient(-45deg, transparent 30%, #666 30%, #666 70%, transparent 70%)',
            opacity: 0.7
          }}
        />
      )}
    </div>
  );
};

export default DeviceManager;
