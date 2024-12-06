// frontend/src/components/DisplayImageBlock.jsx

import React from 'react';
import { Handle } from 'reactflow';

function DisplayImageBlock({ data, isConnectable }) {
  const imageUrl = data.image_url;

  return (
    <div className="ai-block display-image">
      <Handle type="target" position="top" isConnectable={isConnectable} />
      <div className="block-content">
        <h3>Display Image</h3>
        {imageUrl ? (
          <img src={imageUrl} alt="Generated" style={{ maxWidth: '200px' }} />
        ) : (
          <div className="placeholder">Image will appear here...</div>
        )}
      </div>
      <Handle type="source" position="bottom" isConnectable={isConnectable} />
    </div>
  );
}

export default DisplayImageBlock;
