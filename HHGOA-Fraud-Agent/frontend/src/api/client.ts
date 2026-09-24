import axios, { AxiosError } from 'axios';

const BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

export const apiClient = axios.create({
  baseURL: BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor: add dynamic Request-ID
apiClient.interceptors.request.use((config) => {
  const reqId = `req-ui-${Math.random().toString(36).substring(2, 9)}`;
  config.headers['X-Request-ID'] = reqId;
  return config;
});

// Response interceptor: normalize error messages
apiClient.interceptors.response.use(
  (response) => response,
  (error: AxiosError<{ error?: { message?: string; code?: string } }>) => {
    const errorMsg =
      error.response?.data?.error?.message ||
      error.message ||
      'An unexpected error occurred while communicating with the server.';
    return Promise.reject(new Error(errorMsg));
  }
);
