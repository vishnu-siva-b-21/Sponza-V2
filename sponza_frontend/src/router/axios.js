import axios from "axios";
import Swal from "sweetalert2";

const API = axios.create({
  baseURL: "http://127.0.0.1:5000"
});

const showAlert = (message) => {
  Swal.fire({
    icon: "warning",
    title: "Access Denied",
    text: message,
    confirmButtonText: "OK"
  });
};

API.interceptors.request.use(
  async (config) => {
    const accessToken = localStorage.getItem("accessToken");
    if (accessToken) {
      config.headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

API.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      const refreshToken = localStorage.getItem("refreshToken");
      if (refreshToken) {
        try {
          const { data } = await axios.post(
            "http://127.0.0.1:5000/refresh",
            {},
            {
              headers: {
                Authorization: `Bearer ${refreshToken}`
              }
            }
          );
          const newAccessToken = data.access_token;
          localStorage.setItem("accessToken", newAccessToken);
          originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
          return API(originalRequest);
        } catch (refreshError) {
          showAlert("Token refresh failed. Please log in again.");
          localStorage.removeItem("accessToken");
          localStorage.removeItem("refreshToken");
          localStorage.removeItem("userRole");
          window.location.href = "/";
        }
      } else {
        showAlert("No refresh token available. Redirecting to login.");
        localStorage.removeItem("accessToken");
        localStorage.removeItem("refreshToken");
        localStorage.removeItem("userRole");
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  }
);

export default API;
