export const API_ENDPOINTS = {
  orders: {
    create: "orders/create/",
    get: "orders/get/",
    delete: (orderId: number) => `orders/delete/${orderId}/`,
    bulkDelete: "orders/bulk-delete/",
  },
  schedules: {
    get: "schedules/get/",
    generate: "schedules/generate/",
    delete: (scheduleId: number) => `schedules/delete/${scheduleId}/`,
    bulkDelete: "schedules/bulk-delete/",
  },
  auth: {
    login: "auth/login/",
    register: "auth/register/",
    logout: "auth/logout/",
  },
  agvs: {
    base: "agvs/",
  },
  map: {
    importConnections: "map/import-connections/",
    importDirections: "map/import-directions/",
    fetchMapData: "map/get/",
    deleteAllMapData: "map/delete/", // Add this line
  },
};
