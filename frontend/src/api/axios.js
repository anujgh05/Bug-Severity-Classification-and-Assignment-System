import axios from 'axios';

const api = axios.create({
  baseURL: '/api/v1',
  headers: { 'Content-Type': 'application/json' },
});

api.interceptors.request.use((config) => {
  const role = localStorage.getItem('role');
  const developerId = localStorage.getItem('developerId');
  if (role) config.headers['X-User-Role'] = role;
  if (developerId) config.headers['X-Developer-Id'] = developerId;
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    const message =
      error.response?.data?.detail ||
      error.response?.data?.error ||
      error.message ||
      'An unexpected error occurred';
    return Promise.reject(new Error(typeof message === 'string' ? message : JSON.stringify(message)));
  },
);

export const submitBug = (summary, description) =>
  api.post('/bugs/submit', { summary, description });

export const getPendingBugs = () => api.get('/admin/pending');

export const overrideBug = (bugId, severity) =>
  api.put(`/admin/override/${bugId}`, { severity });

export const getDeveloperTasks = (developerId) =>
  api.get(`/developer/${developerId}/tasks`);

export const getDevelopers = () => api.get('/developers');

export default api;
