/**
 * Application routes configuration
 *
 * This file contains a centralized route management system that makes
 * route maintenance, navigation, and configuration easier and more consistent.
 */
import { PageAGVs } from "@/app/admin/agvs/PageAGVs";
import { PageDashboard } from "@/app/admin/dashboard/PageDashboard";
import { PageMap } from "@/app/admin/map/PageMap";
import { PageOrders } from "@/app/admin/orders/PageOrders";
import { LoginPage } from "@/app/auth/LoginPage";
import { RegisterPage } from "@/app/auth/RegisterPage";
import { PageDashboardDemo } from "@/app/demo/dashboard-demo/PageDashboardDemo";
import { HomePage } from "@/app/home/HomePage";
import {
  ChartLine,
  Forklift,
  House,
  ListOrdered,
  LogIn,
  LucideIcon,
  Map,
  UserPlus,
} from "lucide-react";
import { FC } from "react";

/**
 * Route configuration interface
 */
export interface RouteConfig {
  path: string; // Path segment (/home, /login, etc.)
  title: string; // Display title for the route
  icon?: LucideIcon; // Icon to display with the route
  isIndex?: boolean; // Whether this is the default route
  page: FC; // Component to render for this route
}

/**
 * Application routes
 */
export const FRONTEND_ROUTES = {
  home: {
    path: "/home",
    title: "Home",
    isIndex: true,
    icon: House,
    page: HomePage,
  },
  login: {
    path: "/login",
    title: "Login",
    icon: LogIn,
    page: LoginPage,
  },
  register: {
    path: "/register",
    title: "Register",
    icon: UserPlus,
    page: RegisterPage,
  },
  map: {
    path: "/map",
    title: "Map",
    icon: Map,
    page: PageMap,
  },
  agvs: {
    path: "/agvs",
    title: "AGVs",
    icon: Forklift,
    page: PageAGVs,
  },
  orders: {
    path: "/orders",
    title: "Orders",
    icon: ListOrdered,
    page: PageOrders,
  },
  dashboard: {
    path: "/dashboard",
    title: "Dashboard",
    icon: ChartLine,
    page: PageDashboard,
  },
  dashboardDemo: {
    path: "/dashboard-demo",
    title: "Dashboard Demo",
    icon: ChartLine,
    page: PageDashboardDemo,
  },
} as const;

/**
 * Get all routes for navigation and search components
 */
export function getAllRoutes(): RouteConfig[] {
  return Object.values(FRONTEND_ROUTES);
}
