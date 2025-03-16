import { z } from "zod";

export const CreateScheduleZod = z.object({
  schedule_id: z.number(),
  order_id: z.number(),
  order_date: z.string(),
  start_time: z.string(),
  est_end_time: z.string(),
  start_point: z.number(),
  end_point: z.number(),
  load_name: z.string(),
  load_amount: z.number(),
  load_weight: z.number(),
  instruction_set: z.string(),
});

export type CreateScheduleDto = z.infer<typeof CreateScheduleZod>;

export interface Schedule {
  schedule_id: number;
  order_id: number;
  order_date: string;
  start_time: string;
  est_end_time: string;
  start_point: number;
  end_point: number;
  load_name: string;
  load_amount: number;
  load_weight: number;
  instruction_set: string;
}
