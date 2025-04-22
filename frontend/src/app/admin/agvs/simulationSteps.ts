export interface SimulationStep {
  agv_id: number;
  current_node: number;
}

export const simulationSteps: SimulationStep[] = [
  { agv_id: 2, current_node: 17 },
  { agv_id: 2, current_node: 18 },
  { agv_id: 2, current_node: 10 },
  { agv_id: 1, current_node: 7 },
  { agv_id: 1, current_node: 6 },
  { agv_id: 1, current_node: 5 },
  { agv_id: 3, current_node: 32 },
  { agv_id: 3, current_node: 31 },
  { agv_id: 3, current_node: 23 },
  { agv_id: 3, current_node: 15 },
  { agv_id: 1, current_node: 13 },
  { agv_id: 2, current_node: 11 },
  { agv_id: 1, current_node: 21 },
  { agv_id: 2, current_node: 12 },
  { agv_id: 3, current_node: 14 },
  { agv_id: 2, current_node: 13 },
  { agv_id: 3, current_node: 6 },
  { agv_id: 2, current_node: 14 },
  { agv_id: 3, current_node: 14 },
  { agv_id: 2, current_node: 22 },
  { agv_id: 3, current_node: 13 },
  { agv_id: 3, current_node: 12 },
  { agv_id: 3, current_node: 11 },
  { agv_id: 3, current_node: 19 },
];
