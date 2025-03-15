import api from "@/utils/axiosCustomize";

export const importConnections = async (csvData: string) => {
  return api.post("import-connections/", csvData, {
    headers: { "Content-Type": "text/csv" },
  });
};

export const importDirections = async (csvData: string) => {
  return api.post("import-directions/", csvData, {
    headers: { "Content-Type": "text/csv" },
  });
};

export const fetchMapData = async () => {
  const response = await api.get("get-map-data/");
  return response.data;
};
