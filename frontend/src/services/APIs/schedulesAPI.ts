import { Schedule } from "@/types/Schedule.types";
import { API_ENDPOINTS } from "./apiEndpoints";
import { apiService } from "./apiService";

const getSchedules = async (): Promise<Schedule[]> => {
  return apiService.get(API_ENDPOINTS.schedules.get);
};

const generateSchedules = async (
  algorithm: string = "dijkstra",
): Promise<void> => {
  return apiService.post(API_ENDPOINTS.schedules.generate, { algorithm });
};

const deleteSchedule = async (scheduleId: number): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.schedules.delete(scheduleId));
};

const bulkDeleteSchedules = async (scheduleIds: number[]): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.schedules.bulkDelete, {
    schedule_ids: scheduleIds,
  });
};

export { getSchedules, generateSchedules, deleteSchedule, bulkDeleteSchedules };
