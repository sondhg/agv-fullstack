import { z } from "zod";

export const CreateScheduleZod = z.object({
  schedule_id: z.number(),
  order_id: z.number(),
  order_date: z.string(),
  start_time: z.string(),
  est_end_time: z.string(),
  parking_node: z.number(),
  storage_node: z.number(),
  workstation_node: z.number(),
  instruction_set: z.string(),
  cp: z.string().optional(),
  scp: z.string().optional(),
  sp: z.string().optional(),
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
  instruction_set: string;
  cp?: string;
  scp?: string;
  sp?: string;
}
