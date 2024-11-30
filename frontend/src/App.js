// frontend/src/App.js

import React, { useState, useCallback, useEffect } from 'react';
import ReactFlow, { 
  addEdge, 
  Background, 
  MiniMap,
  Controls,
  useNodesState,
  useEdgesState
} from 'reactflow';
import 'reactflow/dist/style.css';
import './styles/App.css';
import './styles/blocks.css';
import './styles/toolbar.css';
import { executeWorkflow } from './services/api';
import { WorkflowProvider } from './context/WorkflowContext';
import { wsService } from './services/websocket';
import WorkflowToolbar from './components/WorkflowToolbar';

// Import your existing components
import GenerateTextBlock from './components/GenerateTextBlock';
import DisplayTextBlock from './components/DisplayTextBlock';

const nodeTypes = {
  generateText: GenerateTextBlock,
  displayText: DisplayTextBlock,
};

function App() {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);
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
    setEdges((eds) => addEdge(params, eds));
  }, [setEdges]);

  const onDragOver = useCallback((event) => {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'move';
  }, []);

  const onDrop = useCallback((event) => {
    event.preventDefault();
    const type = event.dataTransfer.getData('application/reactflow');
    
    if (!type) return;

    // Get the position where the node was dropped
    const reactFlowBounds = document.querySelector('.react-flow').getBoundingClientRect();
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
        imageUrl: ''
      },
    };

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
        inputs[edge.targetHandle || 'input'] = edge.source;
      });
      return {
        id: node.id,
        type: node.type,
        inputs: inputs,
        data: node.data
      };
    });

    const workflow = { blocks }; // Ensure the structure has a 'blocks' key
    const response = await executeWorkflow(workflow);
    setWorkflowId(response.task_id);
    pollTaskStatus(response.task_id);
  } catch (error) {
    setExecutionStatus('Error: ' + error.message);
  }
  setIsExecuting(false);
};


  const pollTaskStatus = async (taskId) => {
    const ws = new WebSocket(`ws://localhost:8000/ws/${taskId}`);
    
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
    <WorkflowProvider>
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
              onDragStart={(e) => e.dataTransfer.setData('application/reactflow', 'generateText')}
            >
              Generate Text
            </div>
            <div 
              className="block-item"
              draggable
              onDragStart={(e) => e.dataTransfer.setData('application/reactflow', 'displayText')}
            >
              Display Text
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
          >
            <Background />
            <Controls />
            <MiniMap />
          </ReactFlow>
          <div className="status-bar">
            {executionStatus && <div className="status-message">{executionStatus}</div>}
            <button 
              className="execute-button" 
              onClick={handleExecuteWorkflow}
              disabled={isExecuting}
            >
              {isExecuting ? 'Executing...' : 'Execute Workflow'}
            </button>
          </div>
        </div>
      </div>
    </WorkflowProvider>
  );
}

export default App;
