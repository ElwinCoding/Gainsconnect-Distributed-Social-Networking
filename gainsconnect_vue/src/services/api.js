// src/services/api.js
import axios from 'axios';

// Determine if we are on localhost
const isLocalhost = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';
// Set the baseURL based on the environment
//const apiBaseURL = isLocalhost ? 'http://127.0.0.1:8000' : 'https://gainsboro-1-14e5c56743f9.herokuapp.com';  // Vic's node
const apiBaseURL = isLocalhost ? 'http://127.0.0.1:8000' : 'https://gainsboro-f5f74d5f43ca.herokuapp.com';  // Elwin's node
//const apiBaseURL = isLocalhost ? 'http://127.0.0.1:8000' : 'https://gainsconnect-elton-f1280be30053.herokuapp.com'; Elton's node
//const apiBaseURL = isLocalhost ? 'http://127.0.0.1:8000' : 'https://gainsconnect-advik-368cb67ab038.herokuapp.com'; Advik's node
//const apiBaseURL = isLocalhost ? 'http://127.0.0.1:8000' : 'https://gainsconnect-sid-d22d31f3cf51.herokuapp.com';  // Sid's node

const api = axios.create({
  baseURL: apiBaseURL, // Your backend URL
});

api.interceptors.response.use(
  response => response,
  async error => {
    const originalRequest = error.config;
    if (error.response.status === 401 && !originalRequest._retry) {
      originalRequest._retry = true;

      try {
        const refreshToken = localStorage.getItem('refresh_token');
        const response = await axios.post(`${apiBaseURL}/api/token/refresh/`, {
          refresh: refreshToken,
        });

        localStorage.setItem('access_token', response.data.access);
        api.defaults.headers['Authorization'] = `Bearer ${response.data.access}`;
        originalRequest.headers['Authorization'] = `Bearer ${response.data.access}`;
        return api(originalRequest);
      } catch (refreshError) {
        console.error("Token refresh failed:", refreshError);
        // Redirect to login if refresh fails
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default api;