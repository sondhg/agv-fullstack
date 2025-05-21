import { CreateOrderDto, Order } from "@/types/Order.types";
import { API_ENDPOINTS } from "./apiEndpoints";
import { apiService } from "./apiService";

const getOrders = async (): Promise<Order[]> => {
  return apiService.get(API_ENDPOINTS.orders.get);
};

const createOrder = async (order: CreateOrderDto): Promise<Order> => {
  return apiService.post(API_ENDPOINTS.orders.create, order);
};

const updateOrder = async (
  order_id: number,
  order: CreateOrderDto,
): Promise<Order> => {
  return apiService.put(API_ENDPOINTS.orders.update(order_id), order);
};

const deleteOrder = async (order_id: number): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.orders.delete(order_id));
};

const createMultipleOrdersBatch = async (
  orders: CreateOrderDto[],
): Promise<Order[]> => {
  return apiService.post(API_ENDPOINTS.orders.create, orders);
};

const bulkDeleteOrders = async (orderIds: number[]): Promise<void> => {
  return apiService.delete(API_ENDPOINTS.orders.bulkDelete, {
    order_ids: orderIds,
  });
};

export {
  bulkDeleteOrders,
  createMultipleOrdersBatch,
  createOrder,
  deleteOrder,
  getOrders,
  updateOrder,
};
