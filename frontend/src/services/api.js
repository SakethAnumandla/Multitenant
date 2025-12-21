import axios from "axios";

const API_BASE_URL =
  process.env.REACT_APP_API_BASE_URL || "http://localhost:5000/api";

// Create axios instance
const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: parseInt(process.env.REACT_APP_API_TIMEOUT) || 10000,
  headers: {
    "Content-Type": "application/json",
  },
});

// Request interceptor - Add JWT token to requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor - Handle errors
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    if (error.response) {
      // Handle 401 - Unauthorized (token expired or invalid)
      if (error.response.status === 401) {
        localStorage.removeItem("token");
        localStorage.removeItem("user");
        window.location.href = "/login";
      }
    }
    return Promise.reject(error);
  }
);

// ==================== ADMIN APIs ====================

export const adminAPI = {
  // Login
  login: (credentials) => api.post("/admin/login", credentials),

  // Tenants
  getTenants: (page = 1, perPage = 10) =>
    api.get(`/admin/tenants?page=${page}&per_page=${perPage}`),
  getTenantById: (id) => api.get(`/admin/tenants/${id}`),
  createTenant: (data) => api.post("/admin/tenants", data),
  updateTenant: (id, data) => api.put(`/admin/tenants/${id}`, data),
  deleteTenant: (id) => api.delete(`/admin/tenants/${id}`),

  // Dashboard
  getDashboard: () => api.get("/admin/dashboard"),
};

// ==================== TENANT APIs ====================

export const tenantAPI = {
  // Login
  login: (credentials) => api.post("/tenant/login", credentials),

  // Profile
  getProfile: () => api.get("/tenant/profile"),
  updateProfile: (data) => api.put("/tenant/profile", data),

  // Users
  getUsers: (page = 1, perPage = 10, role = null) => {
    let url = `/tenant/users?page=${page}&per_page=${perPage}`;
    if (role) url += `&role=${role}`;
    return api.get(url);
  },
  getUserById: (id) => api.get(`/tenant/users/${id}`),
  createUser: (data) => api.post("/tenant/users", data),
  updateUser: (id, data) => api.put(`/tenant/users/${id}`, data),
  deleteUser: (id) => api.delete(`/tenant/users/${id}`),

  // Dashboard
  getDashboard: () => api.get("/tenant/dashboard"),
};

// ==================== USER APIs ====================

export const userAPI = {
  // Login
  login: (credentials) => api.post("/user/login", credentials),
  loginBySlug: (slug, credentials) =>
    api.post(`/user/login/${slug}`, credentials),

  // Registration
  register: (data) => api.post("/user/register", data),

  // Password Management
  resetPassword: (data) => api.post("/user/reset-password", data),
  changePassword: (data) => api.post("/user/change-password", data),

  // Profile
  getProfile: () => api.get("/user/profile"),
  updateProfile: (data) => api.put("/user/profile", data),
};

// ==================== HELPER FUNCTIONS ====================

export const setAuthToken = (token) => {
  if (token) {
    localStorage.setItem("token", token);
  } else {
    localStorage.removeItem("token");
  }
};

export const getAuthToken = () => {
  return localStorage.getItem("token");
};

export const setUser = (user) => {
  if (user) {
    localStorage.setItem("user", JSON.stringify(user));
  } else {
    localStorage.removeItem("user");
  }
};

export const getUser = () => {
  const user = localStorage.getItem("user");
  return user ? JSON.parse(user) : null;
};

export const logout = () => {
  localStorage.removeItem("token");
  localStorage.removeItem("user");
  window.location.href = "/login";
};

export const isAuthenticated = () => {
  return !!getAuthToken();
};

// ==================== TEST APIs ====================

export const testAPI = {
  // Test Management (Tenant/Admin)
  getTests: () => api.get("/test/tests"),
  getTest: (id) => api.get(`/test/tests/${id}`),
  createTest: (data) => api.post("/test/tests", data),
  updateTest: (id, data) => api.put(`/test/tests/${id}`, data),
  deleteTest: (id) => api.delete(`/test/tests/${id}`),

  // Question Management
  getQuestions: (testId) => api.get(`/test/tests/${testId}/questions`),
  createQuestion: (testId, data) => api.post(`/test/tests/${testId}/questions`, data),
  updateQuestion: (questionId, data) => api.put(`/test/questions/${questionId}`, data),
  deleteQuestion: (questionId) => api.delete(`/test/questions/${questionId}`),
  reorderQuestions: (testId, questionOrders) =>
    api.post(`/test/tests/${testId}/questions/reorder`, { question_orders: questionOrders }),

  // Test Taking (User)
  startTest: (testId) => api.post(`/test/tests/${testId}/start`),
  submitAnswer: (responseId, questionId, answer) =>
    api.post(`/test/responses/${responseId}/answers`, {
      question_id: questionId,
      answer: answer,
    }),
  uploadImage: (responseId, imageFile) => {
    const formData = new FormData();
    formData.append("image", imageFile);
    return api.post(`/test/responses/${responseId}/upload-image`, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });
  },
  completeTest: (responseId) => api.post(`/test/responses/${responseId}/complete`),
  getUserResponses: () => api.get("/test/responses"),
  
  // Initialize default test
  initializeDefaultTest: (tenantId) => api.post("/test/initialize-default-test", { tenant_id: tenantId }),
};

export default api;
