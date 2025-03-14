import { format } from "date-fns";
import { startPoints, endPoints } from "./arraysUsedOften";

export const MAX_LOAD_AMOUNT_VALUE = 100;
export const MIN_LOAD_AMOUNT_VALUE = 0;

export const MIN_START_POINT_VALUE = startPoints[0];
export const MAX_START_POINT_VALUE = startPoints[startPoints.length - 1];

export const MIN_END_POINT_VALUE = endPoints[0];
export const MAX_END_POINT_VALUE = endPoints[endPoints.length - 1];

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

export const isStartPointWithinRange = (start_point: number): boolean =>
  MIN_START_POINT_VALUE <= start_point && start_point <= MAX_START_POINT_VALUE;

export const isEndPointWithinRange = (end_point: number): boolean =>
  MIN_END_POINT_VALUE <= end_point && end_point <= MAX_END_POINT_VALUE;

export const isLoadWeightWithinRange = (load_weight: number): boolean =>
  MIN_LOAD_WEIGHT_VALUE <= load_weight && load_weight <= MAX_LOAD_WEIGHT_VALUE;

export const isOrderIdWithinRange = (order_id: number): boolean =>
  MIN_ORDER_ID_VALUE <= order_id && order_id <= MAX_ORDER_ID_VALUE;
