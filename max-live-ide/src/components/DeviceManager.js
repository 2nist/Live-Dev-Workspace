import React, { useState, useEffect, useMemo } from 'react';
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

  return (
    <div className="device-manager-overlay">
      <div className="device-manager">
        {/* Header */}
        <div className="device-manager-header">
          <h2>Device & Script Manager</h2>
          <button className="close-button" onClick={onClose}>✕</button>
        </div>

        {/* Statistics Bar */}
        <div className="status-statistics">
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
        <div className="device-manager-controls">
          <div className="search-section">
            <input
              type="text"
              placeholder="Search devices and scripts..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="search-input"
            />
            <button className="search-button">🔍</button>
          </div>

          <div className="filter-section">
            <select
              value={filterType}
              onChange={(e) => setFilterType(e.target.value)}
              className="filter-select"
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
            >
              <option value="name">Sort by Name</option>
              <option value="type">Sort by Type</option>
              <option value="status">Sort by Status</option>
            </select>

            <button
              className="sort-order-button"
              onClick={() => setSortOrder(prev => prev === 'asc' ? 'desc' : 'asc')}
              title={`Sort ${sortOrder === 'asc' ? 'Descending' : 'Ascending'}`}
            >
              {sortOrder === 'asc' ? '↑' : '↓'}
            </button>
          </div>

          {/* Tag Filter */}
          <div className="tag-section">
            <div className="tag-label">Filter by Tags:</div>
            <div className="tag-list">
              {allTags.map(tag => (
                <button
                  key={tag}
                  className={`tag-button ${selectedTags.includes(tag) ? 'selected' : ''}`}
                  onClick={() => handleTagToggle(tag)}
                >
                  {tag}
                </button>
              ))}
            </div>
          </div>
        </div>

        {/* Device List */}
        <div className="device-list">
          <div className="list-header">
            <span className="column-header name">Name</span>
            <span className="column-header type">Type</span>
            <span className="column-header status">Status</span>
            <span className="column-header tags">Tags</span>
            <span className="column-header actions">Actions</span>
          </div>

          <div className="list-content">
            {filteredAndSortedNodes.map(node => (
              <div key={node.id} className="device-item">
                <div className="device-info">
                  <div className="device-name">
                    <span className="type-icon">{getTypeIcon(node.data.objectType)}</span>
                    <span className="name-text">{node.data.label}</span>
                  </div>
                  
                  <div className="device-type">
                    {node.data.objectType || 'unknown'}
                  </div>
                  
                  <div className="device-status">
                    <span className="status-icon">{getStatusIcon(node.data.status)}</span>
                    <select
                      value={node.data.status || 'disabled'}
                      onChange={(e) => handleStatusChange(node.id, e.target.value)}
                      className="status-select"
                    >
                      <option value="connected">Connected</option>
                      <option value="running">Running</option>
                      <option value="error">Error</option>
                      <option value="disabled">Disabled</option>
                    </select>
                  </div>
                  
                  <div className="device-tags">
                    {node.data.tags && node.data.tags.map(tag => (
                      <span key={tag} className="tag">{tag}</span>
                    ))}
                  </div>
                  
                  <div className="device-actions">
                    <button className="action-button" title="Edit">✏️</button>
                    <button className="action-button" title="Test">🧪</button>
                    <button className="action-button" title="Reset">🔄</button>
                    <button className="action-button danger" title="Remove">🗑️</button>
                  </div>
                </div>

                {/* Expanded Details */}
                {node.data.expanded && (
                  <div className="device-details">
                    <div className="detail-row">
                      <span className="detail-label">ID:</span>
                      <span className="detail-value">{node.id}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">Position:</span>
                      <span className="detail-value">
                        x: {Math.round(node.position.x)}, y: {Math.round(node.position.y)}
                      </span>
                    </div>
                    {node.data.lastError && (
                      <div className="detail-row error">
                        <span className="detail-label">Last Error:</span>
                        <span className="detail-value">{node.data.lastError}</span>
                      </div>
                    )}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Bulk Actions */}
        <div className="bulk-actions">
          <button className="bulk-button">Enable All</button>
          <button className="bulk-button">Disable All</button>
          <button className="bulk-button">Test All</button>
          <button className="bulk-button">Reset All</button>
        </div>
      </div>
    </div>
  );
};

export default DeviceManager;
