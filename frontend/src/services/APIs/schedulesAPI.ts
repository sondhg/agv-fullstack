import { Schedule } from "@/types/Schedule.types";
import api from "@/utils/axiosCustomize";

const SEE_SCHEDULES_URL = "schedule_generate/";
const GENERATE_SCHEDULES_URL = "schedule_generate/generate/";
const DELETE_SCHEDULE_URL = (scheduleId: number) =>
  `schedule_generate/${scheduleId}/delete/`;
const BULK_DELETE_SCHEDULES_URL = "schedule_generate/bulk-delete/";

const getSchedules = async (): Promise<Schedule[]> => {
  try {
    const { data } = await api.get(SEE_SCHEDULES_URL);
    return data;
  } catch (error) {
    console.error(">>> Error fetching schedules:", error);
    throw new Error(">>> Failed to fetch schedules");
  }
};

const generateSchedules = async (
  algorithm: string = "dijkstra",
): Promise<void> => {
  try {
    const { data } = await api.post(GENERATE_SCHEDULES_URL, { algorithm });
    return data;
  } catch (error: any) {
    if (error.response?.status === 400 && error.response?.data?.warning) {
      throw new Error(error.response.data.warning);
    }
    console.error(">>> Error generating schedules:", error);
    throw new Error("Failed to generate schedules");
  }
};

const deleteSchedule = async (scheduleId: number): Promise<void> => {
  try {
    await api.delete(DELETE_SCHEDULE_URL(scheduleId));
  } catch (error) {
    console.error(`>>> Error deleting schedule with ID ${scheduleId}:`, error);
    throw new Error(">>> Failed to delete schedule");
  }
};

const bulkDeleteSchedules = async (scheduleIds: number[]): Promise<void> => {
  try {
    await api.delete(BULK_DELETE_SCHEDULES_URL, {
      data: { schedule_ids: scheduleIds },
    });
  } catch (error) {
    console.error(">>> Error bulk deleting schedules:", error);
    throw new Error(">>> Failed to bulk delete schedules");
  }
};

export { getSchedules, generateSchedules, deleteSchedule, bulkDeleteSchedules };
