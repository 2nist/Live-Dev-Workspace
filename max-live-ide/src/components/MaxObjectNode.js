import React from 'react';
import { Handle, Position } from '@xyflow/react';

const MaxObjectNode = ({ data, isConnectable }) => {
  return (
    <div className="react-flow__node-max-object">
      <Handle
        type="target"
        position={Position.Top}
        isConnectable={isConnectable}
      />
      <div>{data.label}</div>
      <Handle
        type="source"
        position={Position.Bottom}
        isConnectable={isConnectable}
      />
    </div>
  );
};

export default MaxObjectNode;
