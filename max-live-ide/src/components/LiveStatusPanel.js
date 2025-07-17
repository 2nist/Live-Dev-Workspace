import React, { useState, useEffect } from 'react';
import './LiveStatusPanel.css';

const LiveStatusPanel = ({
  liveStatus,
  deviceStatuses,
  scriptStatuses,
  connectionHealth,
  isVisible,
  onToggle
}) => {
  const [expandedSections, setExpandedSections] = useState({
    connection: true,
    devices: false,
    scripts: false,
    performance: false
  });

  const [refreshInterval, setRefreshInterval] = useState(1000);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, refreshInterval);

    return () => clearInterval(interval);
  }, [refreshInterval]);

  const toggleSection = (section) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const getConnectionStatusColor = (connected) => {
    return connected ? '#00ff00' : '#ff4444';
  };

  const getHealthColor = (health) => {
    if (health >= 90) return '#00ff00';
    if (health >= 70) return '#ffff00';
    if (health >= 50) return '#ff8800';
    return '#ff4444';
  };

  const formatLatency = (latency) => {
    if (latency < 10) return `${latency.toFixed(1)}ms`;
    return `${Math.round(latency)}ms`;
  };

  const formatUptime = (uptime) => {
    const hours = Math.floor(uptime / 3600);
    const minutes = Math.floor((uptime % 3600) / 60);
    const seconds = uptime % 60;
    return `${hours}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`;
  };

  if (!isVisible) {
    return (
      <div className="live-status-collapsed">
        <button 
          className="status-toggle-button"
          onClick={onToggle}
          title="Show Live Status"
        >
          📊
        </button>
      </div>
    );
  }

  return (
    <div className="live-status-panel">
      {/* Header */}
      <div className="status-panel-header">
        <h3>Ableton Live Status</h3>
        <div className="header-controls">
          <select
            value={refreshInterval}
            onChange={(e) => setRefreshInterval(Number(e.target.value))}
            className="refresh-select"
          >
            <option value={500}>0.5s</option>
            <option value={1000}>1s</option>
            <option value={2000}>2s</option>
            <option value={5000}>5s</option>
          </select>
          <button 
            className="status-toggle-button"
            onClick={onToggle}
            title="Hide Status Panel"
          >
            ✕
          </button>
        </div>
      </div>

      {/* Connection Status */}
      <div className="status-section">
        <div 
          className="section-header"
          onClick={() => toggleSection('connection')}
        >
          <span className="section-title">Connection</span>
          <span className={`connection-indicator ${liveStatus.connected ? 'connected' : 'disconnected'}`}>
            <div 
              className="indicator-dot"
              style={{ backgroundColor: getConnectionStatusColor(liveStatus.connected) }}
            ></div>
            {liveStatus.connected ? 'Connected' : 'Disconnected'}
          </span>
          <span className="section-chevron">{expandedSections.connection ? '▼' : '▶'}</span>
        </div>
        
        {expandedSections.connection && (
          <div className="section-content">
            <div className="status-grid">
              <div className="status-item">
                <span className="status-label">Health:</span>
                <span 
                  className="status-value"
                  style={{ color: getHealthColor(connectionHealth.overall) }}
                >
                  {connectionHealth.overall}%
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Latency:</span>
                <span className="status-value">
                  {formatLatency(liveStatus.latency || 0)}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Uptime:</span>
                <span className="status-value">
                  {formatUptime(liveStatus.uptime || 0)}
                </span>
              </div>
              <div className="status-item">
                <span className="status-label">Version:</span>
                <span className="status-value">{liveStatus.version || 'Unknown'}</span>
              </div>
            </div>
            
            <div className="connection-details">
              <div className="detail-row">
                <span>WebSocket:</span>
                <span className={connectionHealth.websocket ? 'healthy' : 'unhealthy'}>
                  {connectionHealth.websocket ? '✓' : '✗'}
                </span>
              </div>
              <div className="detail-row">
                <span>HTTP API:</span>
                <span className={connectionHealth.http ? 'healthy' : 'unhealthy'}>
                  {connectionHealth.http ? '✓' : '✗'}
                </span>
              </div>
              <div className="detail-row">
                <span>UDP:</span>
                <span className={connectionHealth.udp ? 'healthy' : 'unhealthy'}>
                  {connectionHealth.udp ? '✓' : '✗'}
                </span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Performance Metrics */}
      <div className="status-section">
        <div 
          className="section-header"
          onClick={() => toggleSection('performance')}
        >
          <span className="section-title">Performance</span>
          <span className="performance-summary">
            CPU: {liveStatus.cpuUsage || 0}%
          </span>
          <span className="section-chevron">{expandedSections.performance ? '▼' : '▶'}</span>
        </div>
        
        {expandedSections.performance && (
          <div className="section-content">
            <div className="performance-meters">
              <div className="meter">
                <div className="meter-label">CPU Usage</div>
                <div className="meter-bar">
                  <div 
                    className="meter-fill"
                    style={{ 
                      width: `${liveStatus.cpuUsage || 0}%`,
                      backgroundColor: getHealthColor(100 - (liveStatus.cpuUsage || 0))
                    }}
                  ></div>
                </div>
                <div className="meter-value">{liveStatus.cpuUsage || 0}%</div>
              </div>
              
              <div className="meter">
                <div className="meter-label">Memory Usage</div>
                <div className="meter-bar">
                  <div 
                    className="meter-fill"
                    style={{ 
                      width: `${liveStatus.memoryUsage || 0}%`,
                      backgroundColor: getHealthColor(100 - (liveStatus.memoryUsage || 0))
                    }}
                  ></div>
                </div>
                <div className="meter-value">{liveStatus.memoryUsage || 0}%</div>
              </div>
              
              <div className="meter">
                <div className="meter-label">Audio Load</div>
                <div className="meter-bar">
                  <div 
                    className="meter-fill"
                    style={{ 
                      width: `${liveStatus.audioLoad || 0}%`,
                      backgroundColor: getHealthColor(100 - (liveStatus.audioLoad || 0))
                    }}
                  ></div>
                </div>
                <div className="meter-value">{liveStatus.audioLoad || 0}%</div>
              </div>
            </div>
            
            <div className="performance-stats">
              <div className="stat">
                <span className="stat-label">Sample Rate:</span>
                <span className="stat-value">{liveStatus.sampleRate || 44100} Hz</span>
              </div>
              <div className="stat">
                <span className="stat-label">Buffer Size:</span>
                <span className="stat-value">{liveStatus.bufferSize || 512} samples</span>
              </div>
              <div className="stat">
                <span className="stat-label">Tempo:</span>
                <span className="stat-value">♩ = {liveStatus.tempo || 120}</span>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Device Status */}
      <div className="status-section">
        <div 
          className="section-header"
          onClick={() => toggleSection('devices')}
        >
          <span className="section-title">Devices</span>
          <span className="device-summary">
            {Object.keys(deviceStatuses || {}).length} devices
          </span>
          <span className="section-chevron">{expandedSections.devices ? '▼' : '▶'}</span>
        </div>
        
        {expandedSections.devices && (
          <div className="section-content">
            <div className="device-list">
              {Object.entries(deviceStatuses || {}).map(([deviceId, status]) => (
                <div key={deviceId} className="device-status-item">
                  <div className="device-info">
                    <span className="device-name">{status.name || deviceId}</span>
                    <span className="device-type">{status.type || 'Unknown'}</span>
                  </div>
                  <div className="device-status-indicators">
                    <span className={`status-indicator ${status.status || 'unknown'}`}>
                      {status.status === 'connected' && '🟢'}
                      {status.status === 'running' && '🟡'}
                      {status.status === 'error' && '🔴'}
                      {status.status === 'disabled' && '⚫'}
                      {!status.status && '⚪'}
                    </span>
                    <span className="status-text">{status.status || 'unknown'}</span>
                  </div>
                </div>
              ))}
              
              {Object.keys(deviceStatuses || {}).length === 0 && (
                <div className="no-devices">No devices found</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Script Status */}
      <div className="status-section">
        <div 
          className="section-header"
          onClick={() => toggleSection('scripts')}
        >
          <span className="section-title">Scripts</span>
          <span className="script-summary">
            {Object.keys(scriptStatuses || {}).length} scripts
          </span>
          <span className="section-chevron">{expandedSections.scripts ? '▼' : '▶'}</span>
        </div>
        
        {expandedSections.scripts && (
          <div className="section-content">
            <div className="script-list">
              {Object.entries(scriptStatuses || {}).map(([scriptId, status]) => (
                <div key={scriptId} className="script-status-item">
                  <div className="script-info">
                    <span className="script-name">{status.name || scriptId}</span>
                    <span className="script-path">{status.path || 'Unknown path'}</span>
                  </div>
                  <div className="script-status-indicators">
                    <span className={`status-indicator ${status.status || 'unknown'}`}>
                      {status.status === 'running' && '🟢'}
                      {status.status === 'error' && '🔴'}
                      {status.status === 'disabled' && '⚫'}
                      {!status.status && '⚪'}
                    </span>
                    <span className="status-text">{status.status || 'unknown'}</span>
                  </div>
                  {status.lastError && (
                    <div className="script-error">{status.lastError}</div>
                  )}
                </div>
              ))}
              
              {Object.keys(scriptStatuses || {}).length === 0 && (
                <div className="no-scripts">No scripts found</div>
              )}
            </div>
          </div>
        )}
      </div>

      {/* Footer */}
      <div className="status-panel-footer">
        <div className="last-update">
          Last updated: {lastUpdate.toLocaleTimeString()}
        </div>
        <div className="footer-actions">
          <button className="footer-button" title="Refresh Now">🔄</button>
          <button className="footer-button" title="Export Status">💾</button>
        </div>
      </div>
    </div>
  );
};

export default LiveStatusPanel;
