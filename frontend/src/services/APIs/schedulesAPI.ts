import { Schedule } from "@/types/Schedule.types";
import api from "@/utils/axiosCustomize";

const SEE_SCHEDULES_URL = "schedule/"; // API endpoint của Hoàng Anh là schedule, không phải schedules
const CREATE_SCHEDULE_URL = "requests_management/schedule/";

const getSchedules = async (): Promise<Schedule[]> => {
  try {
    const { data } = await api.get(SEE_SCHEDULES_URL);
    return data;
  } catch (error) {
    console.error(">>> Error fetching schedules:", error);
    throw new Error(">>> Failed to fetch schedules");
  }
};

const createSchedule = async (): Promise<void> => {
  try {
    const { data } = await api.get(CREATE_SCHEDULE_URL);
    return data;
  } catch (error) {
    console.error(">>> Error creating schedule:", error);
    throw new Error(">>> Failed to create schedule");
  }
};

export { getSchedules, createSchedule };
