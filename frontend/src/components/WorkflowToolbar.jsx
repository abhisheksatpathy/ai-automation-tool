// frontend/src/components/WorkflowToolbar.jsx

import React, { useState } from 'react';
import { useWorkflow } from '../context/WorkflowContext';
import { saveWorkflow, loadWorkflow as apiLoadWorkflow } from '../services/api';

function WorkflowToolbar() {
    const { 
        savedWorkflows, 
        setSavedWorkflows, 
        nodes, 
        edges, 
        setNodes, 
        setEdges 
    } = useWorkflow();
    const [workflowName, setWorkflowName] = useState('');
    const [workflowDescription, setWorkflowDescription] = useState('');
    const [showSaveDialog, setShowSaveDialog] = useState(false);

    const handleSave = async () => {
        if (!workflowName) {
            alert("Please enter a workflow name.");
            return;
        }
        
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

            const workflow = { blocks };
            
            console.log('Saving workflow:', {
                name: workflowName,
                description: workflowDescription,
                workflow: workflow
            });

            const result = await saveWorkflow({
                name: workflowName,
                description: workflowDescription,
                workflow: workflow
            });
            setSavedWorkflows([...savedWorkflows, result]);
            setShowSaveDialog(false);
            alert("Workflow saved successfully!");
            setWorkflowName('');
            setWorkflowDescription(''); // Reset description field
        } catch (error) {
            console.error('Error saving workflow:', error);
            alert("Failed to save workflow: " + error.message);
        }
    };

    const handleLoad = async (workflowId) => {
        if (!workflowId) return; // Do nothing if no workflow is selected

        try {
            const workflow = await apiLoadWorkflow(workflowId);
            console.log('Loaded workflow:', workflow);
            if (workflow.workflow && workflow.workflow.blocks) {
                const loadedBlocks = workflow.workflow.blocks;
                // Reset current nodes and edges
                setNodes([]);
                setEdges([]);

                // Reconstruct nodes and edges from blocks
                loadedBlocks.forEach(block => {
                    const { id, type, inputs, data } = block;
                    const position = { x: 100, y: 100 }; // Default position, or store and retrieve positions
                    const newNode = {
                        id,
                        type,
                        position,
                        data
                    };
                    setNodes(prev => [...prev, newNode]);

                    // Reconstruct edges based on inputs
                    for (const key in inputs) {
                        const source = inputs[key];
                        const target = id;
                        const edgeId = `${source}-${target}`;
                        const newEdge = {
                            id: edgeId,
                            source: source,
                            target: target,
                            type: 'smoothstep', 
                        };
                        setEdges(prev => [...prev, newEdge]);
                    }
                });
                alert("Workflow loaded successfully!");
            } else {
                throw new Error("Invalid workflow format.");
            }
        } catch (error) {
            console.error('Error loading workflow:', error);
            alert("Failed to load workflow: " + error.message);
        }
    };

    return (
        <div className="workflow-toolbar">
            <button onClick={() => setShowSaveDialog(true)}>Save Workflow</button>
            <select onChange={(e) => handleLoad(e.target.value)}>
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
                    <textarea
                        value={workflowDescription}
                        onChange={(e) => setWorkflowDescription(e.target.value)}
                        placeholder="Workflow description"
                    />
                    <div className="dialog-buttons">
                        <button onClick={handleSave}>Save</button>
                        <button onClick={() => setShowSaveDialog(false)}>Cancel</button>
                    </div>
                </div>
            )}
        </div>
    );
}

export default WorkflowToolbar;
