import axios from "axios";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || "http://127.0.0.1:8000/api",
  timeout: 15000,
});

export const getHealth = () => api.get("/health");
export const getStats = () => api.get("/stats");
export const getRisk = () => api.get("/risk");
export const getTransactions = (params = {}) =>
  api.get("/transactions", { params });
export const getTransaction = (transactionId) =>
  api.get(`/transactions/${transactionId}`);
export const simulateTransaction = (body = {}) =>
  api.post("/transactions/simulate", body);
export const predictTransaction = (payload) => api.post("/predict", payload);
export const getModelStatus = () => api.get("/model/status");
export const getModelMetrics = () => api.get("/model/metrics");

export default api;



