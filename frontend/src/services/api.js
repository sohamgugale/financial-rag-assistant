import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export const documentAPI = {
  // Upload document
  uploadDocument: async (file) => {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  // List all documents
  listDocuments: async () => {
    const response = await api.get('/documents');
    return response.data;
  },

  // Get specific document
  getDocument: async (documentId) => {
    const response = await api.get(`/documents/${documentId}`);
    return response.data;
  },

  // Delete document
  deleteDocument: async (documentId) => {
    const response = await api.delete(`/documents/${documentId}`);
    return response.data;
  },

  // Query documents
  queryDocuments: async (queryData) => {
    const response = await api.post('/query', queryData);
    return response.data;
  },

  // Extract insights
  extractInsights: async (insightData) => {
    const response = await api.post('/insights', insightData);
    return response.data;
  },

  // Compare documents
  compareDocuments: async (compareData) => {
    const response = await api.post('/compare', compareData);
    return response.data;
  },

  // Health check
  healthCheck: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api;
