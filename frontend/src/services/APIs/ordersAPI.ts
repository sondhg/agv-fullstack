import { CreateOrderDto, Order } from "@/types/Order.types";
import api from "@/utils/axiosCustomize";

const CREATE_ORDERS_URL = "orders/create/";
const GET_ORDERS_URL = "orders/";
const DELETE_ORDER_URL = (orderId: number) => `orders/${orderId}/delete/`;
const BULK_DELETE_ORDERS_URL = "orders/bulk-delete/";

const getOrders = async (): Promise<Order[]> => {
  try {
    const { data } = await api.get(GET_ORDERS_URL);
    return data;
  } catch (error) {
    console.error(">>> Error fetching orders:", error);
    throw new Error(">>> Failed to fetch orders");
  }
};

const createOrder = async (order: CreateOrderDto): Promise<Order> => {
  try {
    const { data } = await api.post(CREATE_ORDERS_URL, order);
    return data;
  } catch (error) {
    console.error(">>> Error creating order:", error);
    throw new Error(">>> Failed to create order");
  }
};

const updateOrder = async (
  order_id: number,
  order: CreateOrderDto,
): Promise<Order> => {
  try {
    const { data } = await api.put(`${CREATE_ORDERS_URL}${order_id}/`, order); // CREATE_ORDERS_URL already had a slash at the end
    return data;
  } catch (error) {
    console.error(">>> Error updating order:", error);
    throw new Error(">>> Failed to update order");
  }
};

const deleteOrder = async (order_id: number): Promise<void> => {
  try {
    await api.delete(DELETE_ORDER_URL(order_id));
  } catch (error) {
    console.error(`>>> Error deleting order with ID ${order_id}:`, error);
    throw new Error(">>> Failed to delete order");
  }
};

const createMultipleOrdersBatch = async (
  orders: CreateOrderDto[],
): Promise<Order[]> => {
  try {
    const { data } = await api.post(CREATE_ORDERS_URL, orders);
    return data; // Assumes the backend responds with an array of created orders
  } catch (error) {
    console.error(">>> Error creating multiple orders:", error);
    throw new Error(">>> Failed to create multiple orders");
  }
};

const bulkDeleteOrders = async (orderIds: number[]): Promise<void> => {
  try {
    await api.delete(BULK_DELETE_ORDERS_URL, {
      data: { order_ids: orderIds },
    });
  } catch (error) {
    console.error(">>> Error bulk deleting orders:", error);
    throw new Error(">>> Failed to bulk delete orders");
  }
};

export {
  createMultipleOrdersBatch,
  createOrder,
  deleteOrder,
  getOrders,
  updateOrder,
  bulkDeleteOrders,
};
