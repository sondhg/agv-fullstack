import { AGV, CreateAGVDto } from "@/types/AGV.types";
import { API_ENDPOINTS } from "./apiEndpoints";
import { apiService } from "./apiService";

const getAGVs = async (): Promise<AGV[]> => {
  return apiService.get(API_ENDPOINTS.agvs.get);
};

const createAGV = async (data: CreateAGVDto): Promise<AGV> => {
  return apiService.post(API_ENDPOINTS.agvs.create, data);
};

const deleteAGV = async (agvId: number): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.agvs.delete(agvId));
};

const bulkDeleteAGVs = async (agvIds: number[]): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.agvs.bulkDelete, {
    agv_ids: agvIds,
  });
};

const dispatchOrdersToAGVs = async (
  algorithm: string = "dijkstra",
): Promise<void> => {
  return apiService.post(API_ENDPOINTS.agvs.dispatch, { algorithm });
};

const resetAGVs = async (): Promise<{ success: boolean; message: string }> => {
  return apiService.post(API_ENDPOINTS.agvs.reset, {});
};

const scheduleHelloMessage = async (): Promise<AGV[]> => {
  return apiService.get(API_ENDPOINTS.agvs.scheduleHelloMessage);
};

export {
  bulkDeleteAGVs,
  createAGV,
  deleteAGV,
  dispatchOrdersToAGVs,
  getAGVs,
  resetAGVs,
  scheduleHelloMessage,
};
