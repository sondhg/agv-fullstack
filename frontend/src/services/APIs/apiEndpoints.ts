export const API_ENDPOINTS = {
  auth: {
    login: "auth/login/",
    register: "auth/register/",
    logout: "auth/logout/",
  },
  orders: {
    create: "orders/create/",
    get: "orders/get/",
    update: (orderId: number) => `orders/update/${orderId}/`,
    delete: (orderId: number) => `orders/delete/${orderId}/`,
    bulkDelete: "orders/bulk-delete/",
  },
  agvs: {
    create: "agvs/create/",
    get: "agvs/get/",
    delete: (agvId: number) => `agvs/delete/${agvId}/`,
    bulkDelete: "agvs/bulk-delete/",
    dispatch: "agvs/dispatch-orders-to-agvs/",
    reset: "agvs/reset/",
    scheduleHelloMessage: "agvs/schedule-hello-messages/",
  },
  map: {
    importConnections: "map/import-connections/",
    importDirections: "map/import-directions/",
    fetchMapData: "map/get/",
    deleteAllMapData: "map/delete/",
  },
};
