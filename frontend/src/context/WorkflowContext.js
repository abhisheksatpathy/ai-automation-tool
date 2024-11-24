import React, { createContext, useContext, useState } from 'react';

const WorkflowContext = createContext();

export function WorkflowProvider({ children }) {
    const [workflowStatus, setWorkflowStatus] = useState({});
    const [savedWorkflows, setSavedWorkflows] = useState([]);
    const [currentWorkflow, setCurrentWorkflow] = useState(null);

    const value = {
        workflowStatus,
        setWorkflowStatus,
        savedWorkflows,
        setSavedWorkflows,
        currentWorkflow,
        setCurrentWorkflow,
    };

    return (
        <WorkflowContext.Provider value={value}>
            {children}
        </WorkflowContext.Provider>
    );
}

export function useWorkflow() {
    return useContext(WorkflowContext);
}
