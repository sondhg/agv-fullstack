import { AGV, CreateAgvDto } from "@/types/AGV.types";
import { apiService } from "./apiService";
import { API_ENDPOINTS } from "./apiEndpoints";

const getAGVs = async (): Promise<AGV[]> => {
  return apiService.get(API_ENDPOINTS.agvs.base);
};

const createAGV = async (agv: CreateAgvDto): Promise<AGV> => {
  return apiService.post(API_ENDPOINTS.agvs.base, agv);
};

const deleteAGV = async (agv_id: number): Promise<void> => {
  return apiService.delete(`${API_ENDPOINTS.agvs.base}${agv_id}/`);
};

export { deleteAGV, getAGVs, createAGV };
