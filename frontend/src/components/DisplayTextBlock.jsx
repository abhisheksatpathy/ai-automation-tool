// frontend/src/components/DisplayTextBlock.jsx

import React, { useState } from 'react';
import { Handle } from 'reactflow';

function DisplayTextBlock({ data, isConnectable }) {
  const displayText = data.displayedText || data.text || 'Text will appear here...';

  return (
    <div className="ai-block display-text">
      <Handle type="target" position="top" isConnectable={isConnectable} />
      <div className="block-content">
        <h3>Display Text</h3>
        <div 
          className="text-display"
          style={{ 
            padding: '10px',
            border: '1px solid #ddd',
            borderRadius: '4px',
            minHeight: '60px'
          }}
        >
          {displayText}
        </div>
      </div>
      <Handle type="source" position="bottom" isConnectable={isConnectable} />
    </div>
  );
}

export default DisplayTextBlock;
