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

export const loginUser = (usernameOrEmail, password, role = null, developerId = null) =>
  api.post('/auth/login', {
    username_or_email: usernameOrEmail,
    password,
    role,
    developer_id: developerId ? Number(developerId) : null,
  });

export const registerUser = (username, email, password, role = 'user', developerId = null) =>
  api.post('/auth/register', {
    username,
    email,
    password,
    role,
    developer_id: developerId ? Number(developerId) : null,
  });

export const submitBug = (summary, description, reporterUserId = null) =>
  api.post('/bugs/submit', { summary, description, reporter_user_id: reporterUserId });

export const getUserBugs = (userId) => api.get(`/user/${userId}/bugs`);

export const getPendingBugs = () => api.get('/admin/pending');

export const overrideBug = (bugId, severity) =>
  api.put(`/admin/override/${bugId}`, { severity });

export const getDeveloperTasks = (developerId) => api.get(`/developer/${developerId}/tasks`);

export const updateDeveloperBugStatus = (developerId, bugId, status) =>
  api.put(`/developer/${developerId}/bugs/${bugId}/status`, { status });

export const getDevelopers = () => api.get('/developers');

export default api;
