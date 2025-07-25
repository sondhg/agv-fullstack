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
): Promise<{
  success: boolean;
  message: string;
  scheduled_orders?: Array<{
    order_id: number;
    agv_id: number;
    parking_node: number;
    scheduled_time: string;
    seconds_from_now: number;
  }>;
  immediate_orders?: Array<{
    order_id: number;
    agv_id: number;
    parking_node: number;
    status: string;
  }>;
  total_processed?: number;
}> => {
  return apiService.post(API_ENDPOINTS.agvs.dispatch, { algorithm });
};

const resetAGVs = async (): Promise<{ success: boolean; message: string }> => {
  return apiService.post(API_ENDPOINTS.agvs.reset, {});
};

const scheduleHelloMessage = async (): Promise<AGV[]> => {
  return apiService.get(API_ENDPOINTS.agvs.scheduleHelloMessage);
};

const createAGVsViaCSV = async (
  csvFile: File,
): Promise<{ success: boolean; message: string; created_agvs: AGV[] }> => {
  const formData = new FormData();
  formData.append("csv_file", csvFile);

  // For FormData, we need to let the browser set the Content-Type header
  // to include the proper boundary parameter
  return apiService.post(API_ENDPOINTS.agvs.createViaCSV, formData, {
    headers: {
      "Content-Type": undefined, // This allows axios to set the proper Content-Type with boundary
    },
  });
};

export {
  bulkDeleteAGVs,
  createAGV,
  createAGVsViaCSV,
  deleteAGV,
  dispatchOrdersToAGVs,
  getAGVs,
  resetAGVs,
  scheduleHelloMessage,
};
