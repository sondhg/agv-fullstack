import api from "@/utils/axiosCustomize";

export const fetchMapData = async () => {
  try {
    const response = await api.get("map/");
    return response.data;
  } catch (error) {
    console.error("Error fetching map data:", error);
    throw error;
  }
};
