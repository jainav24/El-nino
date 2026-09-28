import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token && config.headers) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.data?.detail && Array.isArray(error.response.data.detail)) {
      // Convert FastAPI validation array to a single comma-separated string
      error.response.data.detail = error.response.data.detail.map((err: any) => `${err.loc.slice(-1)}: ${err.msg}`).join(', ');
    }
    return Promise.reject(error);
  }
);

export const dashboardApi = {
  getStats: () => api.get('/dashboard/stats').then((res) => res.data),
  getAnalytics: () => api.get('/dashboard/analytics').then((res) => res.data),
};

export const mlApi = {
  train: () => api.post('/ml/train').then((res) => res.data),
  predict: (data: any) => api.post('/ml/predict', data).then((res) => res.data), // Update to use correct route
  kaplanMeier: (groupBy?: string) => api.get('/ml/kaplan-meier', { params: { group_by: groupBy } }).then((res) => res.data),
  getVersions: () => api.get('/ml/versions').then((res) => res.data),
  getPolicyContext: (policyId: string) => api.get(`/ml/policy-context/${policyId}`).then((res) => res.data),
};

export const dataApi = {
  validateCsv: (formData: FormData) => api.post('/data/validate-csv', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((res) => res.data),
  storeCsv: (formData: FormData) => api.post('/data/store-csv', formData, { headers: { 'Content-Type': 'multipart/form-data' } }).then((res) => res.data),
  seedDemo: () => api.post('/data/seed').then((res) => res.data),
};

export const advisoryApi = {
  getAdvisory: (state: string, crop: string, season: string) =>
    api.get('/advisory', { params: { state, crop, season } }).then((res) => res.data),
  getEnsoStatus: () => api.get('/advisory/enso-status').then((res) => res.data),
  getSupportedStates: () => api.get('/advisory/states').then((res) => res.data),
};

export const coreApi = {
  getFarmers: () => api.get('/farmers').then((res) => res.data),
  getPolicies: () => api.get('/policies').then((res) => res.data),
  getClaims: () => api.get('/claims').then((res) => res.data),
  getWeather: () => api.get('/weather').then((res) => res.data),
  getEnso: () => api.get('/enso').then((res) => res.data),
  getHealth: () => api.get('/health').then((res) => res.data),
  calculateQuote: (data: any) => api.post('/insurance/quote', data).then((res) => res.data),
};
