import { z } from "zod";

export const CreateOrderZod = z.object({
  order_id: z.preprocess(
    (order_id) => parseInt(order_id as string, 10),
    z.number(),
  ),
  load_name: z.string(),
  load_amount: z.preprocess(
    (load_amount) => parseFloat(load_amount as string),
    z.number(),
  ),
  load_weight: z.preprocess(
    (load_weight) => parseFloat(load_weight as string),
    z.number(),
  ),
  start_point: z.preprocess(
    (start_point) => parseInt(start_point as string, 10),
    z.number(),
  ),
  end_point: z.preprocess(
    (end_point) => parseInt(end_point as string, 10),
    z.number(),
  ),
  start_time: z.string(),
  order_date: z.string(),
  user_name: z.string(),
});

export type CreateOrderDto = z.infer<typeof CreateOrderZod>;

export interface Order {
  order_id: number;
  order_date: string;
  start_time: string;
  start_point: number;
  end_point: number;
  load_name: string;
  load_amount: number;
  load_weight: number;
  user_name: string;
}
