import React from 'react';
import { Handle, Position } from '@xyflow/react';
import { IconCode, IconCheck } from '@tabler/icons-react';

const MaxObjectNode = ({ data, isConnectable, selected }) => {
  // Detect JavaScript objects
  const isJSObject = data.label?.startsWith('js') || 
                     data.label?.startsWith('jsui') ||
                     data.objectType === 'javascript';
  
  const hasCode = data.jsCode && data.jsCode.trim().length > 0;

  return (
    <div className={`react-flow__node-max-object ${isJSObject ? 'js-object' : ''} ${selected ? 'selected' : ''}`}>
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      
      <div className="object-content">
        <span className="object-label">{data.label}</span>
        
        {/* Code indicator for JS objects */}
        {isJSObject && (
          <div className="code-indicator">
            {hasCode ? (
              <IconCheck size={12} className="has-code-icon" title="Has code" />
            ) : (
              <IconCode size={12} className="no-code-icon" title="Click to add code" />
            )}
          </div>
        )}
      </div>
      
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default MaxObjectNode;
