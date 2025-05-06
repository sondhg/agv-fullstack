import api from "@/utils/axiosCustomize";
import { AxiosError } from "axios"; // Import AxiosError type

export const apiService = {
  get: async <T>(url: string): Promise<T> => {
    try {
      const { data } = await api.get(url);
      return data;
    } catch (error) {
      if (error instanceof AxiosError) {
        // Log the backend error message
        console.error(
          `>>> Error fetching data from ${url}:`,
          error.response?.data,
        );
        throw new Error(error.response?.data?.error || "Failed to fetch data");
      } else {
        console.error(`>>> Error fetching data from ${url}:`, error);
        throw new Error("Failed to fetch data");
      }
    }
  },

  post: async <T, U>(url: string, payload: U, config?: object): Promise<T> => {
    try {
      const { data } = await api.post(url, payload, config);
      return data;
    } catch (error) {
      if (error instanceof AxiosError) {
        // Log the backend error message
        console.error(
          `>>> Error posting data to ${url}:`,
          error.response?.data,
        );
        // Pass through the specific error message from the backend
        throw new Error(
          error.response?.data?.detail ||
            error.response?.data?.error ||
            "Failed to post data",
        );
      } else {
        console.error(`>>> Error posting data to ${url}:`, error);
        throw new Error("Failed to post data");
      }
    }
  },

  put: async <T, U>(url: string, payload: U): Promise<T> => {
    try {
      const { data } = await api.put(url, payload);
      return data;
    } catch (error) {
      if (error instanceof AxiosError) {
        // Log the backend error message
        console.error(
          `>>> Error updating data at ${url}:`,
          error.response?.data,
        );
        throw new Error(error.response?.data?.error || "Failed to update data");
      } else {
        console.error(`>>> Error updating data at ${url}:`, error);
        throw new Error("Failed to update data");
      }
    }
  },

  delete: async (
    url: string,
    payload?: Record<string, unknown>,
  ): Promise<void> => {
    try {
      await api.delete(url, { data: payload });
    } catch (error) {
      if (error instanceof AxiosError) {
        // Log the backend error message
        console.error(
          `>>> Error deleting data at ${url}:`,
          error.response?.data,
        );
        throw new Error(error.response?.data?.error || "Failed to delete data");
      } else {
        console.error(`>>> Error deleting data at ${url}:`, error);
        throw new Error("Failed to delete data");
      }
    }
  },
};
