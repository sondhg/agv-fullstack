import { z } from "zod";

export const CreateOrderZod = z.object({
  order_id: z.preprocess(
    (order_id) => parseInt(order_id as string, 10),
    z.number(),
  ),
  order_date: z.string(),
  start_time: z.string(),
  parking_node: z.preprocess(
    (parking_node) => parseInt(parking_node as string, 10),
    z.number(),
  ),
  storage_node: z.preprocess(
    (storage_node) => parseInt(storage_node as string, 10),
    z.number(),
  ),
  workstation_node: z.preprocess(
    (workstation_node) => parseInt(workstation_node as string, 10),
    z.number(),
  ),
});

export type CreateOrderDto = z.infer<typeof CreateOrderZod>;

export interface Order {
  order_id: number;
  order_date: string;
  start_time: string;
  parking_node: number;
  workstation_node: number;
  storage_node: number;
}
