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
  initial_path: z.string(),
  residual_path: z.string(),
  cp: z.string().optional(),
  scp: z.string().optional(),
  sp: z.record(z.string(), z.number()).optional(), // Simplified SP structure
  state: z.number().optional(),
  spare_flag: z.boolean().optional(),
  traveling_info: z
    .object({
      v_c: z.number().nullable().optional(),
      v_n: z.number().nullable().optional(),
      v_r: z.number().nullable().optional(),
    })
    .optional(),
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
  initial_path: string;
  residual_path: string;
  cp?: string;
  scp?: string;
  sp?: Record<string, number>; // Simplified SP structure
  state?: number; // 0: idle, 1: moving, 2: waiting
  spare_flag?: boolean; // Indicates if AGV has spare points
  traveling_info?: {
    v_c: number | null; // Current position
    v_n: number | null; // Next position
    v_r: number | null; // Reserved position
  };
}
