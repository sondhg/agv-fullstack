import { z } from "zod";

export const CreateAgvZod = z.object({
  agv_id: z.preprocess((agv_id) => parseInt(agv_id as string, 10), z.number()),
  guidance_type: z.string(),
  max_battery: z.preprocess(
    (max_battery) => parseInt(max_battery as string, 10),
    z.number(),
  ),
  max_load: z.preprocess(
    (max_load) => parseInt(max_load as string, 10),
    z.number(),
  ),
  max_speed: z.preprocess(
    (max_speed) => parseInt(max_speed as string, 10),
    z.number(),
  ),
});

export type CreateAgvDto = z.infer<typeof CreateAgvZod>;

export interface AGV {
  agv_id: number;
  guidance_type: string;
  max_battery: number;
  max_load: number;
  max_speed: number;
  is_connected: boolean;
  is_active: boolean;
  is_busy: boolean;
  error: string;
}
