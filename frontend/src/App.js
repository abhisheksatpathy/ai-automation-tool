// frontend/src/App.js

import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  MiniMap,
  Controls,
} from 'reactflow';
import 'reactflow/dist/style.css';
import './styles/App.css';
import './styles/blocks.css';
import './styles/toolbar.css';
import { executeWorkflow } from './services/api';
import { WorkflowProvider, useWorkflow } from './context/WorkflowContext';
import { wsService } from './services/websocket';
import WorkflowToolbar from './components/WorkflowToolbar';
import { getWebSocketUrl } from './utils/websocketUrl';
import GenerateTextBlock from './components/GenerateTextBlock';
import DisplayTextBlock from './components/DisplayTextBlock';
import GenerateImageBlock from './components/GenerateImageBlock';
import DisplayImageBlock from './components/DisplayImageBlock';
import TextToSpeechBlock from './components/TextToSpeechBlock';

const nodeTypes = {
  generateText: GenerateTextBlock,
  displayText: DisplayTextBlock,
  generateImage: GenerateImageBlock,
  displayImage: DisplayImageBlock,
  textToSpeech: TextToSpeechBlock,
};

function Flow() {
  const { nodes, setNodes, onNodesChange, edges, setEdges, onEdgesChange } = useWorkflow();
  const [isExecuting, setIsExecuting] = useState(false);
  const [executionStatus, setExecutionStatus] = useState(null);
  const [workflowId, setWorkflowId] = useState(null);

  useEffect(() => {
    if (workflowId) {
      wsService.connect(workflowId);
      return () => wsService.disconnect();
    }
  }, [workflowId]);

  const onConnect = useCallback((params) => {
    console.log("Connecting edge:", params);
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');

    console.log("onDrop called with type:", type);

    if (!type) {
      console.log("Dropped item has no type");
      return;
    }

    // Get the position where the node was dropped
    const reactFlowBounds = document.querySelector('.flow-container').getBoundingClientRect();
    const position = {
      x: event.clientX - reactFlowBounds.left,
      y: event.clientY - reactFlowBounds.top,
    };

    const newNode = {
      id: `${type}-${nodes.length + 1}`,
      type,
      position,
      data: { 
        label: `${type} node`,
        prompt: '',  // Add default values for node data
        params: {},
        text: '',
        image_url: ''
      },
    };

    console.log("Adding new node:", newNode);
    setNodes((nds) => nds.concat(newNode));
  }, [nodes, setNodes]);

  const handleExecuteWorkflow = async () => {
    setIsExecuting(true);
    setExecutionStatus('Executing workflow...');
    try {
      const blocks = nodes.map(node => {
        const incomingEdges = edges.filter(edge => edge.target === node.id);
        const inputs = {};
        incomingEdges.forEach(edge => {
          // Assuming single input per block; adjust if multiple inputs are possible
          inputs['input'] = edge.source;
        });
        return {
          id: node.id,
          type: node.type,
          inputs: inputs,
          data: node.data
        };
      });

      const workflow = { blocks }; // Ensure the structure has a 'blocks' key

      console.log('Executing workflow:', workflow);

      const response = await executeWorkflow(workflow);
      setWorkflowId(response.task_id);
      pollTaskStatus(response.task_id);
    } catch (error) {
      setExecutionStatus('Error: ' + error.message);
      console.error('Execution error:', error);
    }
    setIsExecuting(false);
  };

  const pollTaskStatus = async (taskId) => {
    const wsUrl = getWebSocketUrl(`/ws/${taskId}`);
    console.log(`Connecting to WebSocket at ${wsUrl}`);

    const ws = new WebSocket(wsUrl);
    
    ws.onopen = () => {
      console.log('WebSocket connected');
    };
    
    ws.onmessage = (event) => {
      const status = JSON.parse(event.data);
      console.log('Received status:', status);
      
      if (status.state === 'SUCCESS') {
        setExecutionStatus('Workflow completed successfully!');
        setIsExecuting(false);
        updateNodesWithResults(status.result);
        ws.close();
      } else if (status.state === 'FAILURE') {
        setExecutionStatus('Workflow failed: ' + status.error);
        setIsExecuting(false);
        ws.close();
      }
    };
    
    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setExecutionStatus('Error in workflow execution');
      setIsExecuting(false);
    };
  };

  const updateNodesWithResults = (results) => {
    setNodes(nodes.map(node => {
      if (results[node.id]) {
        return {
          ...node,
          data: {
            ...node.data,
            ...results[node.id]
          }
        };
      }
      return node;
    }));
  };

  return (
    <div className="app-container">
      <WorkflowToolbar />
      <div className="sidebar">
        <div className="sidebar-header">
          <h3>AI Blocks</h3>
        </div>
        <div className="blocks-container">
          <div 
            className="block-item"
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('application/reactflow', 'generateText');
              console.log("Drag Start: generateText");
            }}
          >
            Generate Text
          </div>
          <div 
            className="block-item"
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('application/reactflow', 'displayText');
              console.log("Drag Start: displayText");
            }}
          >
            Display Text
          </div>
          <div 
            className="block-item"
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('application/reactflow', 'generateImage');
              console.log("Drag Start: generateImage");
            }}
          >
            Generate Image
          </div>
          <div 
            className="block-item"
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('application/reactflow', 'displayImage');
              console.log("Drag Start: displayImage");
            }}
          >
            Display Image
          </div>
          <div 
            className="block-item"
            draggable
            onDragStart={(e) => {
              e.dataTransfer.setData('application/reactflow', 'textToSpeech');
              console.log("Drag Start: textToSpeech");
            }}
          >
            Text To Speech
          </div>
        </div>
      </div>
      <div className="flow-container">
        <ReactFlow
          nodes={nodes}
          edges={edges}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          onConnect={onConnect}
          onDragOver={onDragOver}
          onDrop={onDrop}
          nodeTypes={nodeTypes}
          fitView
          fitViewOnInIt
        >
          <Background />
          <Controls />
          <MiniMap />
        </ReactFlow>
        <button 
          className="execute-button" 
          onClick={handleExecuteWorkflow}
          disabled={isExecuting}
        >
          {isExecuting ? 'Executing...' : 'Execute Workflow'}
        </button>
        <div className="status-bar">
          {executionStatus && <div className="status-message">{executionStatus}</div>}
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <WorkflowProvider>
      <Flow />
    </WorkflowProvider>
  );
}

export default App;
