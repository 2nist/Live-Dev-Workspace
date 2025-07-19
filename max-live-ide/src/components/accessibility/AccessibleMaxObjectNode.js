import React, { useRef, useEffect, useState } from 'react';
import { announceToScreenReader } from './AccessibilityHooks';

/**
 * Accessible Max Object Node Component
 * Enhanced with full keyboard navigation, ARIA support, and screen reader compatibility
 */
const AccessibleMaxObjectNode = ({ 
  data, 
  isConnectable, 
  selected, 
  onSelect,
  onDelete,
  onEditProperties,
  ...props 
}) => {
  const nodeRef = useRef(null);
  const [isExpanded, setIsExpanded] = useState(false);
  const [connectionCount, setConnectionCount] = useState({ inputs: 0, outputs: 0 });
  const [isHovered, setIsHovered] = useState(false);
  
  // Update connection counts when data changes
  useEffect(() => {
    setConnectionCount({
      inputs: data.inputs?.length || 0,
      outputs: data.outputs?.length || 0
    });
  }, [data.inputs, data.outputs]);
  
  // Generate accessible description
  const getAccessibleDescription = () => {
    const type = data.objectType || 'utility';
    const status = data.status || 'disconnected';
    const connections = `${connectionCount.inputs} inputs, ${connectionCount.outputs} outputs`;
    
    return `${data.label} - ${type} object, ${status}, ${connections}`;
  };
  
  // Announce status changes to screen readers
  useEffect(() => {
    if (data.status) {
      const announcement = `${data.label} status changed to ${data.status}`;
      announceToScreenReader(announcement);
    }
  }, [data.status, data.label]);
  
  // Handle keyboard interactions
  const handleKeyDown = (event) => {
    switch (event.key) {
      case 'Enter':
      case ' ':
        event.preventDefault();
        if (onSelect) {
          onSelect(data.id);
          announceToScreenReader(`Selected ${data.label}`);
        }
        break;
        
      case 'i':
      case 'I':
        event.preventDefault();
        setIsExpanded(!isExpanded);
        announceToScreenReader(
          `${data.label} information ${isExpanded ? 'collapsed' : 'expanded'}`
        );
        break;
        
      case 'p':
      case 'P':
        event.preventDefault();
        if (onEditProperties) {
          onEditProperties(data.id);
          announceToScreenReader(`Opening properties for ${data.label}`);
        }
        break;
        
      case 'Delete':
      case 'Backspace':
        if (selected && onDelete) {
          event.preventDefault();
          onDelete(data.id);
          announceToScreenReader(`Deleted ${data.label}`);
        }
        break;
        
      case 'ArrowUp':
      case 'ArrowDown':
      case 'ArrowLeft':
      case 'ArrowRight':
        // Let parent handle navigation
        break;
        
      default:
        break;
    }
  };
  
  // Handle mouse interactions
  const handleClick = (event) => {
    event.preventDefault();
    if (onSelect) {
      onSelect(data.id);
    }
  };
  
  const handleDoubleClick = (event) => {
    event.preventDefault();
    if (onEditProperties) {
      onEditProperties(data.id);
    }
  };
  
  // Generate unique IDs for accessibility
  const nodeId = `max-object-${data.id}`;
  const descriptionId = `${nodeId}-description`;
  const statusId = `${nodeId}-status`;
  
  return (
    <div
      ref={nodeRef}
      id={nodeId}
      className={`max-object-node ${data.objectType} ${selected ? 'selected' : ''} ${isHovered ? 'hovered' : ''}`}
      role="button"
      tabIndex={0}
      aria-label={getAccessibleDescription()}
      aria-selected={selected}
      aria-expanded={isExpanded}
      aria-describedby={`${descriptionId} ${statusId}`}
      aria-keyshortcuts="Enter Space i p Delete"
      onKeyDown={handleKeyDown}
      onClick={handleClick}
      onDoubleClick={handleDoubleClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      data-testid={`max-object-${data.label}`}
    >
      {/* Main object label */}
      <div className="object-label" aria-hidden="true">
        {data.label}
      </div>
      
      {/* Status indicator with accessible text */}
      <div 
        id={statusId}
        className="object-status" 
        aria-label={`Status: ${data.status}`}
        role="status"
      >
        <span 
          className={`status-dot ${data.status}`} 
          aria-hidden="true"
        ></span>
        <span className="sr-only">Status: {data.status}</span>
      </div>
      
      {/* Object type badge */}
      {data.objectType && (
        <div className="object-type-badge" aria-hidden="true">
          {data.objectType}
        </div>
      )}
      
      {/* Connection handles with accessible labels */}
      {data.inputs?.map((input, index) => (
        <div
          key={`input-${index}`}
          className="react-flow__handle react-flow__handle-top input-handle"
          style={{ left: `${(index + 1) * (100 / (data.inputs.length + 1))}%` }}
          role="button"
          tabIndex={-1}
          aria-label={`Input ${index + 1}: ${input.name || input.type || 'signal'}`}
          aria-describedby={`${nodeId}-input-${index}-desc`}
          data-testid={`input-${index}`}
        >
          <span 
            id={`${nodeId}-input-${index}-desc`}
            className="sr-only"
          >
            {`Input connection point for ${input.name || input.type || 'signal'}`}
          </span>
        </div>
      ))}
      
      {data.outputs?.map((output, index) => (
        <div
          key={`output-${index}`}
          className="react-flow__handle react-flow__handle-bottom output-handle"
          style={{ left: `${(index + 1) * (100 / (data.outputs.length + 1))}%` }}
          role="button"
          tabIndex={-1}
          aria-label={`Output ${index + 1}: ${output.name || output.type || 'signal'}`}
          aria-describedby={`${nodeId}-output-${index}-desc`}
          data-testid={`output-${index}`}
        >
          <span 
            id={`${nodeId}-output-${index}-desc`}
            className="sr-only"
          >
            {`Output connection point for ${output.name || output.type || 'signal'}`}
          </span>
        </div>
      ))}
      
      {/* Expanded information panel */}
      {isExpanded && (
        <div 
          className="object-info-panel"
          role="region"
          aria-label={`Information for ${data.label}`}
          aria-expanded={true}
        >
          <div className="info-section">
            <strong>Type:</strong> {data.objectType}
          </div>
          <div className="info-section">
            <strong>Status:</strong> {data.status}
          </div>
          {data.description && (
            <div className="info-section">
              <strong>Description:</strong> {data.description}
            </div>
          )}
          {data.tags && data.tags.length > 0 && (
            <div className="info-section">
              <strong>Tags:</strong> {data.tags.join(', ')}
            </div>
          )}
          {data.parameters && Object.keys(data.parameters).length > 0 && (
            <div className="info-section">
              <strong>Parameters:</strong>
              <ul className="parameter-list">
                {Object.entries(data.parameters).map(([key, value]) => (
                  <li key={key}>
                    {key}: {String(value)}
                  </li>
                ))}
              </ul>
            </div>
          )}
          
          {/* Action buttons */}
          <div className="info-actions">
            <button
              className="btn-sm btn-secondary"
              onClick={(e) => {
                e.stopPropagation();
                if (onEditProperties) {
                  onEditProperties(data.id);
                }
              }}
              aria-label={`Edit properties for ${data.label}`}
            >
              Edit Properties
            </button>
            {selected && (
              <button
                className="btn-sm btn-danger"
                onClick={(e) => {
                  e.stopPropagation();
                  if (onDelete) {
                    onDelete(data.id);
                  }
                }}
                aria-label={`Delete ${data.label}`}
              >
                Delete
              </button>
            )}
          </div>
        </div>
      )}
      
      {/* Hidden description for screen readers */}
      <div id={descriptionId} className="sr-only">
        {getAccessibleDescription()}
        {selected ? ' (selected)' : ''}
        {isExpanded ? ' (expanded)' : ''}
        . Press Enter to select, I for info, P for properties
        {selected ? ', Delete to remove' : ''}
      </div>
      
      {/* Keyboard shortcut hints (visible on focus) */}
      <div className="keyboard-hints" aria-hidden="true">
        <div className="hint">Enter/Space: Select</div>
        <div className="hint">I: Toggle Info</div>
        <div className="hint">P: Properties</div>
        {selected && <div className="hint">Del: Delete</div>}
      </div>
    </div>
  );
};

export default AccessibleMaxObjectNode;
