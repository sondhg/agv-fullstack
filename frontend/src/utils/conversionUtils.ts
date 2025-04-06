import { format } from "date-fns";
import { parkingNodes, endPoints } from "./arraysUsedOften";

export const MAX_LOAD_AMOUNT_VALUE = 100;
export const MIN_LOAD_AMOUNT_VALUE = 0;

export const MIN_PARKING_NODE_VALUE = parkingNodes[0];
export const MAX_PARKING_NODE_VALUE = parkingNodes[parkingNodes.length - 1];

export const MIN_WORKSTATION_NODE_VALUE = endPoints[0];
export const MAX_WORKSTATION_NODE_VALUE = endPoints[endPoints.length - 1];

export const MIN_LOAD_WEIGHT_VALUE = 0;
export const MAX_LOAD_WEIGHT_VALUE = 1000;

export const MIN_ORDER_ID_VALUE = 1;
export const MAX_ORDER_ID_VALUE = 1000;

// change strings like "12,34" to numbers like 12.34
export const convertStringToNumber = (amount: string): number =>
  parseFloat(amount.replace(",", "."));

export const convertDateToString = (date: Date): string =>
  format(date, "yyyy-MM-dd");

export const isLoadAmountWithinRange = (load_amount: number): boolean =>
  MIN_LOAD_AMOUNT_VALUE <= load_amount && load_amount <= MAX_LOAD_AMOUNT_VALUE;

export const isStartPointWithinRange = (parking_node: number): boolean =>
  MIN_PARKING_NODE_VALUE <= parking_node && parking_node <= MAX_PARKING_NODE_VALUE;

export const isEndPointWithinRange = (workstation_node: number): boolean =>
  MIN_WORKSTATION_NODE_VALUE <= workstation_node && workstation_node <= MAX_WORKSTATION_NODE_VALUE;

export const isLoadWeightWithinRange = (load_weight: number): boolean =>
  MIN_LOAD_WEIGHT_VALUE <= load_weight && load_weight <= MAX_LOAD_WEIGHT_VALUE;

export const isOrderIdWithinRange = (order_id: number): boolean =>
  MIN_ORDER_ID_VALUE <= order_id && order_id <= MAX_ORDER_ID_VALUE;
