import api from "@/utils/axiosCustomize";

export const apiService = {
  get: async <T>(url: string): Promise<T> => {
    try {
      const { data } = await api.get(url);
      return data;
    } catch (error) {
      console.error(`>>> Error fetching data from ${url}:`, error);
      throw new Error("Failed to fetch data");
    }
  },

  post: async <T, U>(
    url: string,
    payload: U,
    config?: object, // Add this optional parameter
  ): Promise<T> => {
    try {
      const { data } = await api.post(url, payload, config); // Pass config to Axios
      return data;
    } catch (error) {
      console.error(`>>> Error posting data to ${url}:`, error);
      throw new Error("Failed to post data");
    }
  },

  put: async <T, U>(url: string, payload: U): Promise<T> => {
    try {
      const { data } = await api.put(url, payload);
      return data;
    } catch (error) {
      console.error(`>>> Error updating data at ${url}:`, error);
      throw new Error("Failed to update data");
    }
  },

  delete: async (url: string, payload?: Record<string, unknown>): Promise<void> => {
    try {
      await api.delete(url, { data: payload });
    } catch (error) {
      console.error(`>>> Error deleting data at ${url}:`, error);
      throw new Error("Failed to delete data");
    }
  },
};
