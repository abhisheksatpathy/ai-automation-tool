// frontend/src/components/GenerateTextBlock.jsx

import React, { useState } from 'react';
import { Handle } from 'reactflow';

function GenerateTextBlock({ data, isConnectable }) {
  const [prompt, setPrompt] = useState(data.prompt || '');

  const handlePromptChange = (e) => {
    setPrompt(e.target.value);
    data.prompt = e.target.value; // Save to node data
  };

  return (
    <div className="ai-block generate-text">
      <Handle type="target" position="top" isConnectable={isConnectable} />
      <div className="block-content">
        <h3>Generate Text</h3>
        <textarea
          value={prompt}
          onChange={handlePromptChange}
          placeholder="Enter your prompt..."
        />
      </div>
      <Handle type="source" position="bottom" isConnectable={isConnectable} />
    </div>
  );
}

export default GenerateTextBlock;
