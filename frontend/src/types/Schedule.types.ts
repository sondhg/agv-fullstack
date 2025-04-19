import { z } from "zod";
import { AGV } from "./AGV.types";

export const CreateScheduleZod = z.object({
  schedule_id: z.number(),
  order_id: z.number(),
  order_date: z.string(),
  start_time: z.string(),
  est_end_time: z.string(),
  parking_node: z.number(),
  storage_node: z.number(),
  workstation_node: z.number(),
  initial_path: z.array(z.number()),
  residual_path: z.array(z.number()),
  cp: z.array(z.number()),
  scp: z.array(z.number()),
});

export type CreateScheduleDto = z.infer<typeof CreateScheduleZod>;

export interface Schedule {
  schedule_id: number;
  order_id: number;
  order_date: string;
  start_time: string;
  est_end_time: string;
  parking_node: number;
  storage_node: number;
  workstation_node: number;
  assigned_agv: AGV | null;
  initial_path: number[];
  residual_path: number[];
  cp: number[];
  scp: number[];
}
