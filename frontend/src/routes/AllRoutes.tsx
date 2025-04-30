import { PageAGVs } from "@/app/admin/agvs/PageAGVs";
import { PageDashboard } from "@/app/admin/dashboard/PageDashboard";
import { PageMap } from "@/app/admin/map/PageMap";
import { PageOrders } from "@/app/admin/orders/PageOrders";
import { LoginPage } from "@/app/auth/LoginPage";
import { RegisterPage } from "@/app/auth/RegisterPage";
import { PageDashboardDemo } from "@/app/demo/dashboard-demo/PageDashboardDemo";
import { HomePage } from "@/app/home/HomePage";
import Layout from "@/app/layout";
import {
  ADMIN_AGVS,
  ADMIN_BASE,
  ADMIN_DASHBOARD,
  ADMIN_MAP,
  ADMIN_ORDERS,
  DEMO_BASE,
  DEMO_DASHBOARD,
  HOME,
  LOGIN,
  REGISTER,
} from "@/constants/routes";
import { Suspense } from "react";
import { BrowserRouter, Navigate, Route, Routes } from "react-router-dom";
import { NotFound } from "./NotFound";
import { PrivateRoute } from "./PrivateRoute";

export function AllRoutes() {
  return (
    <BrowserRouter>
      <Suspense fallback={<div>Loading...</div>}>
        <Routes>
          {/* Routes that require Layout with sidebar */}
          <Route element={<Layout />}>
            <Route path={HOME} element={<HomePage />} />
            <Route path={DEMO_BASE}>
              <Route
                path={DEMO_DASHBOARD.replace(`${DEMO_BASE}/`, "")}
                element={<PageDashboardDemo />}
              />
            </Route>
            <Route path={ADMIN_BASE} element={<PrivateRoute />}>
              <Route
                path={ADMIN_ORDERS.replace(`${ADMIN_BASE}/`, "")}
                element={<PageOrders />}
              />
              <Route
                path={ADMIN_DASHBOARD.replace(`${ADMIN_BASE}/`, "")}
                element={<PageDashboard />}
              />
              <Route
                path={ADMIN_MAP.replace(`${ADMIN_BASE}/`, "")}
                element={<PageMap />}
              />
              <Route
                path={ADMIN_AGVS.replace(`${ADMIN_BASE}/`, "")}
                element={<PageAGVs />}
              />
            </Route>
          </Route>

          {/* Routes that do not require Layout with sidebar */}
          <Route path="/" element={<Navigate to={HOME} />} />
          <Route path={LOGIN} element={<LoginPage />} />
          <Route path={REGISTER} element={<RegisterPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
