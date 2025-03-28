import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

// Create axios instance with error handling
const api = axios.create({
  baseURL: `${API_URL}/api`,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: false,
  timeout: 15000, // 15 second timeout
});

// Add response interceptor for error handling
api.interceptors.response.use(
  (response) => response,
  (error) => {
    console.error('API Error:', error);
    
    // Handle specific error cases
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (!error.response) {
      console.error('Network error - no response received');
    } else {
      console.error(`Error ${error.response.status}: ${error.response.statusText}`);
    }
    
    return Promise.reject(error);
  }
);

// Add request interceptor for authentication
api.interceptors.request.use(
  (config) => {
    // Add authorization header if token exists in localStorage
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// API endpoints
const endpoints = {
  // Authentication
  auth: {
    register: (data: { email: string; password: string; displayName?: string }) => 
      api.post('/auth/register', data),
    verifyToken: (token: string) => 
      api.post('/auth/verify-token', { token }),
  },
  
  // Content
  content: {
    upload: (formData: FormData, config?: any) => 
      api.post('/content/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
        ...config,
      }),
    analyze: (contentId: string) => 
      api.post(`/content/analyze/${contentId}`),
    getSegments: (contentId: string) => 
      api.get(`/content/segments/${contentId}`),
    createVideo: (data: { contentId: string; templateId: string; segments: string[]; options?: any }) => 
      api.post('/content/create-video', data),
    getTemplates: () => 
      api.get('/content/templates'),
    getContent: (contentId: string) => 
      api.get(`/content/${contentId}`),
    listContent: (params?: { page?: number; limit?: number; type?: string }) => 
      api.get('/content', { params }),
  },
  
  // Analytics
  analytics: {
    getPerformance: (contentId: string) => 
      api.get(`/analytics/performance/${contentId}`),
    getTrends: (params?: { period?: string; platform?: string }) => 
      api.get('/analytics/trends', { params }),
    getEngagementPrediction: (contentId: string) => 
      api.get(`/analytics/engagement-prediction/${contentId}`),
  },
  
  // User
  user: {
    getBrandAssets: () => 
      api.get('/users/brand-assets'),
    uploadBrandAsset: (formData: FormData) => 
      api.post('/users/brand-assets', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }),
    updateProfile: (data: { displayName?: string; preferences?: any }) => 
      api.put('/users/profile', data),
    getProfile: () => 
      api.get('/users/profile'),
  },
};

export default {
  api,
  endpoints,
};
