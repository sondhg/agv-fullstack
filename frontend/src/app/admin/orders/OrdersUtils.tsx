import { CreateOrderDto } from "@/types/Order.types";

// Function to get the current date in the format YYYY-MM-DD
export const getCurrentDate = (): string => {
  const today = new Date();
  const year = today.getFullYear();
  const month = String(today.getMonth() + 1).padStart(2, "0");
  const day = String(today.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

// Function to calculate the start time at least minutesFromNow minutes from current time
export const getStartTime = (minutesFromNow: number): string => {
  const baseTime = new Date();
  baseTime.setSeconds(0);
  baseTime.setMinutes(baseTime.getMinutes() + 1);
  baseTime.setMinutes(baseTime.getMinutes() + (minutesFromNow - 1));

  const hours = String(baseTime.getHours()).padStart(2, "0");
  const minutes = String(baseTime.getMinutes()).padStart(2, "0");

  return `${hours}:${minutes}:00`;
};

// Generate example orders data
export const generateExampleOrders = (
  example: "example1and2" | "example3",
): CreateOrderDto[] => {
  const currentDate = getCurrentDate();

  if (example === "example1and2") {
    return [
      {
        order_id: 1,
        order_date: currentDate,
        start_time: getStartTime(1),
        parking_node: 7,
        storage_node: 15,
        workstation_node: 23,
      },
      {
        order_id: 2,
        order_date: currentDate,
        start_time: getStartTime(2),
        parking_node: 19,
        storage_node: 11,
        workstation_node: 16,
      },
      {
        order_id: 3,
        order_date: currentDate,
        start_time: getStartTime(3),
        parking_node: 13,
        storage_node: 11,
        workstation_node: 9,
      },
    ];
  } else {
    return [
      {
        order_id: 1,
        order_date: currentDate,
        start_time: getStartTime(1),
        parking_node: 8,
        storage_node: 5,
        workstation_node: 29,
      },
      {
        order_id: 2,
        order_date: currentDate,
        start_time: getStartTime(2),
        parking_node: 9,
        storage_node: 10,
        workstation_node: 30,
      },
      {
        order_id: 3,
        order_date: currentDate,
        start_time: getStartTime(3),
        parking_node: 16,
        storage_node: 15,
        workstation_node: 19,
      },
    ];
  }
};
