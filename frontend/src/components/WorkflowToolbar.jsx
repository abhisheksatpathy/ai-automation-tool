import React, { useState } from 'react';
import { useWorkflow } from '../context/WorkflowContext';
import { saveWorkflow, loadWorkflow } from '../services/api';

function WorkflowToolbar() {
    const { currentWorkflow, savedWorkflows, setSavedWorkflows } = useWorkflow();
    const [workflowName, setWorkflowName] = useState('');
    const [showSaveDialog, setShowSaveDialog] = useState(false);

    const handleSave = async () => {
        if (!workflowName) return;
        
        try {
            const result = await saveWorkflow({
                name: workflowName,
                workflow: currentWorkflow
            });
            setSavedWorkflows([...savedWorkflows, result]);
            setShowSaveDialog(false);
        } catch (error) {
            console.error('Error saving workflow:', error);
        }
    };

    return (
        <div className="workflow-toolbar">
            <button onClick={() => setShowSaveDialog(true)}>Save Workflow</button>
            <select onChange={(e) => loadWorkflow(e.target.value)}>
                <option value="">Load Workflow</option>
                {savedWorkflows.map(workflow => (
                    <option key={workflow.id} value={workflow.id}>
                        {workflow.name}
                    </option>
                ))}
            </select>
            
            {showSaveDialog && (
                <div className="save-dialog">
                    <input
                        type="text"
                        value={workflowName}
                        onChange={(e) => setWorkflowName(e.target.value)}
                        placeholder="Workflow name"
                    />
                    <button onClick={handleSave}>Save</button>
                    <button onClick={() => setShowSaveDialog(false)}>Cancel</button>
                </div>
            )}
        </div>
    );
}

export default WorkflowToolbar;
