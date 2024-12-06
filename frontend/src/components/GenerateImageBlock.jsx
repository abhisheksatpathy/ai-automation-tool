// frontend/src/components/GenerateImageBlock.jsx

import React, { useState } from 'react';
import { Handle } from 'reactflow';

function GenerateImageBlock({ data, isConnectable }) {
  const [prompt, setPrompt] = useState(data.prompt || '');

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
    data.prompt = e.target.value; // Save to node data
  };

  return (
    <div className="ai-block generate-image">
      <Handle type="target" position="top" isConnectable={isConnectable} />
      <div className="block-content">
        <h3>Generate Image</h3>
        <textarea
          value={prompt}
          onChange={handlePromptChange}
          placeholder="Enter your image prompt..."
        />
      </div>
      <Handle type="source" position="bottom" isConnectable={isConnectable} />
    </div>
  );
}

export default GenerateImageBlock;
