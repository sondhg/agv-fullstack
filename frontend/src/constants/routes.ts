/**
 * Application routes constants
 *
 * This file contains all the routes used in the application.
 * Using constants ensures consistency across the application and
 * makes route management easier.
 */

// Base routes
export const HOME = "/home";
export const LOGIN = "/login";
export const REGISTER = "/register";

// Admin routes
export const ADMIN_BASE = "/admin";
export const ADMIN_MAP = `${ADMIN_BASE}/map`;
export const ADMIN_AGVS = `${ADMIN_BASE}/agvs`;
export const ADMIN_ORDERS = `${ADMIN_BASE}/orders`;
export const ADMIN_DASHBOARD = `${ADMIN_BASE}/dashboard`;

// Demo routes
export const DEMO_BASE = "/demo";
export const DEMO_DASHBOARD = `${DEMO_BASE}/dashboard-demo`;

// Route objects for components that need title and path
export const ROUTES = {
  // Base routes
  HOME: { title: "Home", path: HOME },
  LOGIN: { title: "Login", path: LOGIN },
  REGISTER: { title: "Register", path: REGISTER },

  // Admin routes
  ADMIN_MAP: { title: "Map", path: ADMIN_MAP },
  ADMIN_AGVS: { title: "AGVs", path: ADMIN_AGVS },
  ADMIN_ORDERS: { title: "Orders", path: ADMIN_ORDERS },
  ADMIN_DASHBOARD: { title: "Dashboard", path: ADMIN_DASHBOARD },

  // Demo routes
  DEMO_DASHBOARD: { title: "Dashboard Demo", path: DEMO_DASHBOARD },
};
