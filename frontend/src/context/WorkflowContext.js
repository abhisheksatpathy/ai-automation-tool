// frontend/src/context/WorkflowContext.js

import React, { createContext, useContext } from 'react';
import { useNodesState, useEdgesState } from 'reactflow';

// Create the context
const WorkflowContext = createContext();

// WorkflowProvider component
export function WorkflowProvider({ children }) {
    // Existing state
    const [workflowStatus, setWorkflowStatus] = React.useState({});
    const [savedWorkflows, setSavedWorkflows] = React.useState([]);
    const [currentWorkflow, setCurrentWorkflow] = React.useState(null);
    
    // New state for nodes and edges
    const [nodes, setNodes, onNodesChange] = useNodesState([]);
    const [edges, setEdges, onEdgesChange] = useEdgesState([]);

    // Context value
    const value = {
        workflowStatus,
        setWorkflowStatus,
        savedWorkflows,
        setSavedWorkflows,
        currentWorkflow,
        setCurrentWorkflow,
        nodes,
        setNodes,
        onNodesChange,
        edges,
        setEdges,
        onEdgesChange,
    };

    return (
        <WorkflowContext.Provider value={value}>
            {children}
        </WorkflowContext.Provider>
    );
}

// Custom hook to use the context
export function useWorkflow() {
    return useContext(WorkflowContext);
}
