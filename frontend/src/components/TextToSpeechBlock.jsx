import React from 'react';
import { Handle } from 'reactflow';

function TextToSpeechBlock({ data, isConnectable }) {
  const audioUrl = data.audio_url; // This should be the full URL with SAS token

  return (
    <div className="ai-block text-to-speech">
      <Handle type="target" position="top" isConnectable={isConnectable} />
      <div className="block-content">
        <h3>Text To Speech</h3>
        {audioUrl ? (
          <audio controls>
            <source src={audioUrl} type="audio/mpeg" />
            Your browser does not support the audio element.
          </audio>
        ) : (
          <div>Audio will appear here...</div>
        )}
      </div>
      <Handle type="source" position="bottom" isConnectable={isConnectable} />
    </div>
  );
}

export default TextToSpeechBlock;
