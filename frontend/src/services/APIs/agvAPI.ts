import { AGV, CreateAgvDto } from "@/types/AGV.types";
import api from "@/utils/axiosCustomize";

const AGVS_URL = "agvs/";

const getAGVs = async (): Promise<AGV[]> => {
  try {
    const { data } = await api.get(AGVS_URL);
    return data;
  } catch (error) {
    console.error(">>> Error fetching AGVs:", error);
    throw new Error(">>> Failed to fetch AGVs");
  }
};

const createAGV = async (agv: CreateAgvDto): Promise<AGV> => {
  try {
    const { data } = await api.post(AGVS_URL, agv);
    return data;
  } catch (error) {
    console.error(">>> Error creating AGV:", error);
    throw new Error(">>> Failed to create AGV");
  }
};

const deleteAGV = async (agv_id: number): Promise<void> => {
  try {
    await api.delete(`${AGVS_URL}${agv_id}/`);
  } catch (error) {
    console.error(">>> Error deleting AGV:", error);
    throw new Error(">>> Failed to delete AGV");
  }
};

export { deleteAGV, getAGVs, createAGV };
