import { apiService } from "./apiService";
import { API_ENDPOINTS } from "./apiEndpoints";
import { AxiosResponse } from "axios";

export const importConnections = async (
  csvData: string,
): Promise<AxiosResponse<Record<string, unknown>, unknown>> => {
  return apiService.post(
    API_ENDPOINTS.map.importConnections,
    csvData,
    { headers: { "Content-Type": "text/csv" } }, // Pass headers as config
  );
};

export const importDirections = async (
  csvData: string,
): Promise<AxiosResponse<Record<string, unknown>, unknown>> => {
  return apiService.post(
    API_ENDPOINTS.map.importDirections,
    csvData,
    { headers: { "Content-Type": "text/csv" } }, // Pass headers as config
  );
};

export const fetchMapData = async () => {
  return apiService.get(API_ENDPOINTS.map.fetchMapData);
};

export const deleteAllMapData = async (): Promise<
  AxiosResponse<Record<string, unknown>, unknown>
> => {
  return apiService.post(API_ENDPOINTS.map.deleteAllMapData, {}); // Send a POST request with an empty payload
};
