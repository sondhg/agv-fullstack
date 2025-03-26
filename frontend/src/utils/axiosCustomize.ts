import axios from "axios";
import { store } from "../redux/store";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://localhost:8000/api/",
  headers: {
    "content-type": "application/json",
  },
});

// Add a request interceptor
api.interceptors.request.use(
  (config) => {
    const access_token = store?.getState()?.user?.account?.access_token;
    if (access_token) {
      config.headers["Authorization"] = `Bearer ${access_token}`;
    }
    return config;
  },
  (error) => Promise.reject(error),
);

// // Add a response interceptor
// api.interceptors.response.use(
//   (response) => response?.data ?? response,
//   (error) => {
//     if (error?.response?.data) {
//       return Promise.reject(error.response.data);
//     }
//     return Promise.reject(error);
//   },
// );

export default api;
