import { z } from "zod";
import { Order } from "./Order.types";

// Define motion state enum to match Python constants
export enum AGVMotionState {
  IDLE = 0,
  MOVING = 1,
  WAITING = 2,
}

export enum AGVJourneyPhase {
  OUTBOUND = 0,
  RETURN = 1,
}

export const CreateAgvZod = z.object({
  agv_id: z.preprocess((agv_id) => parseInt(agv_id as string, 10), z.number()),
  preferred_parking_node: z.preprocess(
    (preferred_parking_node) => parseInt(preferred_parking_node as string, 10),
    z.number(),
  ),
});

export type CreateAgvDto = z.infer<typeof CreateAgvZod>;

export interface AGV {
  agv_id: number;
  preferred_parking_node: number;
  current_node: number | null;
  next_node: number | null;
  reserved_node: number | null;
  previous_node: number | null;
  direction_change: number | null;
  motion_state: AGVMotionState;
  journey_phase: AGVJourneyPhase;
  spare_flag: boolean;
  backup_nodes: Record<string, number>;
  initial_path: number[];
  remaining_path: number[];
  outbound_path: number[];
  return_path: number[];
  common_nodes: number[];
  adjacent_common_nodes: number[];
  active_order: Order | null; // We'll store the order ID
  active_order_info: Order | null; // Detailed order information from serializer
}

export interface CreateAGVDto {
  agv_id: number;
  preferred_parking_node: number;
}
