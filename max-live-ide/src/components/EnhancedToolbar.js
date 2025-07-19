import React, { useState, useCallback } from 'react';
import './EnhancedToolbar.css';

const EnhancedToolbar = ({
  onSearch,
  onDeviceManager,
  onTestResults,
  onZoomToFit,
  onZoomToSelection,
  selectedCount,
  liveStatus,
  onNewPatch,
  onOpenPatch,
  onSavePatch,
  onExportToLive,
  onUndo,
  onRedo,
  onStop,
  onLibraryToggle,
  onParameterEditor
}) => {
  const [isRecording, setIsRecording] = useState(false);
  const [isPlaying, setIsPlaying] = useState(false);

  const handlePlayPause = useCallback(() => {
    setIsPlaying(!isPlaying);
    // Implement play/pause logic
    console.log('Play/Pause clicked');
  }, [isPlaying]);

  const handleRecord = useCallback(() => {
    setIsRecording(!isRecording);
    // Implement record logic
    console.log('Record clicked');
  }, [isRecording]);

  const handleStop = useCallback(() => {
    setIsPlaying(false);
    setIsRecording(false);
    if (onStop) onStop();
    console.log('Stop clicked');
  }, [onStop]);

  const handleNewPatch = useCallback(() => {
    if (onNewPatch) {
      onNewPatch();
    } else {
      console.log('New patch clicked');
      alert('New patch functionality not yet implemented');
    }
  }, [onNewPatch]);

  const handleOpenPatch = useCallback(() => {
    if (onOpenPatch) {
      onOpenPatch();
    } else {
      console.log('Open patch clicked');
      alert('Open patch functionality not yet implemented');
    }
  }, [onOpenPatch]);

  const handleSavePatch = useCallback(() => {
    if (onSavePatch) {
      onSavePatch();
    } else {
      console.log('Save patch clicked');
      alert('Save patch functionality not yet implemented');
    }
  }, [onSavePatch]);

  const handleExportToLive = useCallback(() => {
    if (onExportToLive) {
      onExportToLive();
    } else {
      console.log('Export to Live clicked');
      alert('Export to Live functionality not yet implemented');
    }
  }, [onExportToLive]);

  const handleUndo = useCallback(() => {
    if (onUndo) {
      onUndo();
    } else {
      console.log('Undo clicked');
      alert('Undo functionality not yet implemented');
    }
  }, [onUndo]);

  const handleRedo = useCallback(() => {
    if (onRedo) {
      onRedo();
    } else {
      console.log('Redo clicked');
      alert('Redo functionality not yet implemented');
    }
  }, [onRedo]);

  const handleLibraryToggle = useCallback(() => {
    if (onLibraryToggle) {
      onLibraryToggle();
    } else {
      console.log('Library toggle clicked');
      alert('Object Library functionality not yet implemented');
    }
  }, [onLibraryToggle]);

  const handleParameterEditor = useCallback(() => {
    if (onParameterEditor) {
      onParameterEditor();
    } else {
      console.log('Parameter editor clicked');
      alert('Parameter Editor functionality not yet implemented');
    }
  }, [onParameterEditor]);

  return (
    <div className="enhanced-toolbar">
      {/* Left Section - File Operations */}
      <div className="toolbar-section toolbar-left">
        <div className="toolbar-group">
          <button 
            className="toolbar-button" 
            onClick={handleNewPatch}
            title="New Patch (Ctrl+N)"
          >
            📄
          </button>
          <button 
            className="toolbar-button" 
            onClick={handleOpenPatch}
            title="Open Patch (Ctrl+O)"
          >
            📂
          </button>
          <button 
            className="toolbar-button" 
            onClick={handleSavePatch}
            title="Save Patch (Ctrl+S)"
          >
            💾
          </button>
          <button 
            className="toolbar-button" 
            onClick={handleExportToLive}
            title="Export to Live"
          >
            📤
          </button>
        </div>
        
        <div className="toolbar-separator"></div>
        
        <div className="toolbar-group">
          <button 
            className="toolbar-button" 
            onClick={handleUndo}
            title="Undo (Ctrl+Z)"
          >
            ↶
          </button>
          <button 
            className="toolbar-button" 
            onClick={handleRedo}
            title="Redo (Ctrl+Y)"
          >
            ↷
          </button>
        </div>
      </div>
      
      {/* Center Section - Transport and View Controls */}
      <div className="toolbar-section toolbar-center">
        <div className="toolbar-group transport-controls">
          <button 
            className={`toolbar-button transport-button ${isRecording ? 'recording' : ''}`}
            onClick={handleRecord}
            title="Record"
          >
            ⏺
          </button>
          <button 
            className={`toolbar-button transport-button ${isPlaying ? 'playing' : ''}`}
            onClick={handlePlayPause}
            title="Play/Pause"
          >
            {isPlaying ? '⏸' : '▶'}
          </button>
          <button 
            className="toolbar-button transport-button" 
            onClick={handleStop}
            title="Stop"
          >
            ⏹
          </button>
        </div>
        
        <div className="toolbar-separator"></div>
        
        <div className="toolbar-group view-controls">
          <button 
            className="toolbar-button"
            onClick={onZoomToFit}
            title="Zoom to Fit (Ctrl+1)"
          >
            🔍📐
          </button>
          <button 
            className="toolbar-button"
            onClick={onZoomToSelection}
            disabled={selectedCount === 0}
            title={`Zoom to Selection (${selectedCount} selected) (Ctrl+2)`}
          >
            🎯
          </button>
          <button 
            className="toolbar-button"
            onClick={onSearch}
            title="Search Objects (Ctrl+F)"
          >
            🔍
          </button>
        </div>
      </div>
      
      {/* Right Section - Panel Toggles and Status */}
      <div className="toolbar-section toolbar-right">
        <div className="toolbar-group panel-toggles">
          <button 
            className="toolbar-button"
            onClick={onDeviceManager}
            title="Device Manager (Ctrl+D)"
          >
            🎛️
          </button>
          <button 
            className="toolbar-button"
            onClick={onTestResults}
            title="Test Results (Ctrl+T)"
          >
            🧪
          </button>
          <button 
            className="toolbar-button"
            onClick={handleLibraryToggle}
            title="Object Library"
          >
            📚
          </button>
          <button 
            className="toolbar-button"
            onClick={handleParameterEditor}
            title="Parameter Editor"
          >
            ⚙️
          </button>
        </div>
        
        <div className="toolbar-separator"></div>
        
        <div className="toolbar-group status-group">
          <div className="live-connection-status">
            <div className={`connection-indicator ${liveStatus.connected ? 'connected' : 'disconnected'}`}>
              <div className="indicator-dot"></div>
              <span className="indicator-text">
                {liveStatus.connected ? 'Live Connected' : 'Live Disconnected'}
              </span>
            </div>
            {liveStatus.connected && (
              <div className="live-info">
                <span className="live-tempo">♩ = {liveStatus.tempo || 120}</span>
                <span className="live-time">{liveStatus.playPosition || '0.0.0'}</span>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Quick Stats Bar */}
      <div className="quick-stats">
        <span className="stat-item">Objects: {liveStatus.objectCount || 0}</span>
        <span className="stat-item">CPU: {liveStatus.cpuUsage || 0}%</span>
        <span className="stat-item">Latency: {liveStatus.latency || 0}ms</span>
        {selectedCount > 0 && (
          <span className="stat-item selected">Selected: {selectedCount}</span>
        )}
      </div>
    </div>
  );
};

export default EnhancedToolbar;
