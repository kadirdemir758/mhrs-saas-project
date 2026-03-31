import axios from 'axios';

// MHRS Python (FastAPI) Backend API adresi
const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request Interceptor: JWT Token'i otomatik olarak her isteğe ekler.
// Böylece Depends(get_current_user) olan rotalara güvenli erişebiliriz.
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
