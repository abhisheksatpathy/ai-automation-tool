import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000';

export const executeWorkflow = async (workflow) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/execute-workflow`, workflow);
    return response.data;
  } catch (error) {
    console.error('Error details:', error.response.data);
    throw new Error('Failed to execute workflow: ' + error.message);
  }
};

export const getTaskStatus = async (taskId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/task-status/${taskId}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to get task status: ' + error.message);
  }
};

export const saveWorkflow = async (workflowData) => {
  try {
    const response = await axios.post(`${API_BASE_URL}/workflows/save`, workflowData);
    return response.data;
  } catch (error) {
    throw new Error('Failed to save workflow: ' + error.message);
  }
};

export const loadWorkflow = async (workflowId) => {
  try {
    const response = await axios.get(`${API_BASE_URL}/workflows/${workflowId}`);
    return response.data;
  } catch (error) {
    throw new Error('Failed to load workflow: ' + error.message);
  }
};
