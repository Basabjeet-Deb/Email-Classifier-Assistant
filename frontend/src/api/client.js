import axios from 'axios';

const api = axios.create({
  baseURL: '/api',
  headers: {
    'Content-Type': 'application/json',
  },
});

export const emailAPI = {
  getStatus: () => api.get('/status'),
  
  scanEmails: (data) => api.post('/scan', data),
  
  deleteEmails: (data) => api.post('/delete', data),
  
  archiveEmails: (data) => api.post('/archive', data),
  
  getAnalytics: (accountId, days = 30) => 
    api.get(`/analytics/${accountId}?days=${days}`),
  
  retrainTfidf: () => api.post('/retrain-tfidf'),
  
  authenticate: () => api.post('/auth'),
};

export default api;
