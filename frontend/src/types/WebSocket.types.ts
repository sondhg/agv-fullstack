export interface WebSocketData {
  car_id: number;
  agv_state: number;
  agv_speed: number;
  agv_battery: number;
  previous_waypoint: number;
  next_waypoint: number;
  time_stamp: string;
  distance_sum: number;
  distance: number;
}
