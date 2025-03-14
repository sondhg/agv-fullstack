import { PageAGVs } from "@/app/admin/AGVs/PageAGVs";
import { PageDashboard } from "@/app/admin/dashboard/PageDashboard";
import { PageOrders } from "@/app/admin/orders/PageOrders";
import { PageSchedules } from "@/app/admin/schedules/PageSchedules";
import { LoginPage } from "@/app/auth/LoginPage";
import { RegisterPage } from "@/app/auth/RegisterPage";
import { PageDashboardDemo } from "@/app/demo/dashboard-demo/PageDashboardDemo";
import { PageSchedulesDemo } from "@/app/demo/schedules-demo/PageSchedulesDemo";
import { HomePage } from "@/app/home/HomePage";
import Layout from "@/app/layout";
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
            <Route path="/home" element={<HomePage />} />
            <Route path="/demo">
              <Route path="dashboard-demo" element={<PageDashboardDemo />} />
              <Route path="schedules-demo" element={<PageSchedulesDemo />} />
            </Route>
            <Route path="/admin" element={<PrivateRoute />}>
              <Route path="agvs" element={<PageAGVs />} />
              <Route path="orders" element={<PageOrders />} />
              <Route path="schedules" element={<PageSchedules />} />
              <Route path="dashboard" element={<PageDashboard />} />
            </Route>
          </Route>

          {/* Routes that do not require Layout with sidebar */}
          <Route path="/" element={<Navigate to="/home" />} />
          <Route path="/login" element={<LoginPage />} />
          <Route path="/register" element={<RegisterPage />} />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
