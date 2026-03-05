import axios from 'axios';

// Use environment variable for API URL, fallback to relative path for development
const API_URL = import.meta.env.VITE_API_URL || '';

const api = axios.create({
  baseURL: API_URL ? `${API_URL}/api` : '/api',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
});

export const emailAPI = {
  getStatus: () => api.get('/status'),
  
  scanEmails: (data) => api.post('/scan', data),
  
  deleteEmails: (data) => api.post('/delete', data),
  
  archiveEmails: (data) => api.post('/archive', data),
  
  getAnalytics: (accountId, days = 30) => 
    api.get(`/analytics/${accountId}?days=${days}`),
  
  retrainTfidf: () => api.post('/retrain-tfidf'),
  
  // New OAuth flow
  startAuth: () => api.get('/auth/login'),
  
  // Legacy endpoint (deprecated)
  authenticate: () => api.post('/auth'),
};

export default api;
