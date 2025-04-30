import Layout from "@/app/layout";
import { FRONTEND_ROUTES } from "@/routes/routes";
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
            <Route
              path={FRONTEND_ROUTES.home.path}
              element={<FRONTEND_ROUTES.home.page />}
            />
            <Route
              path={FRONTEND_ROUTES.dashboardDemo.path}
              element={<FRONTEND_ROUTES.dashboardDemo.page />}
            />

            {/* Protected routes */}
            <Route element={<PrivateRoute />}>
              <Route
                path={FRONTEND_ROUTES.orders.path}
                element={<FRONTEND_ROUTES.orders.page />}
              />
              <Route
                path={FRONTEND_ROUTES.dashboard.path}
                element={<FRONTEND_ROUTES.dashboard.page />}
              />
              <Route
                path={FRONTEND_ROUTES.map.path}
                element={<FRONTEND_ROUTES.map.page />}
              />
              <Route
                path={FRONTEND_ROUTES.agvs.path}
                element={<FRONTEND_ROUTES.agvs.page />}
              />
            </Route>
          </Route>

          {/* Routes that do not require Layout with sidebar */}
          <Route
            path="/"
            element={<Navigate to={FRONTEND_ROUTES.home.path} />}
          />
          <Route
            path={FRONTEND_ROUTES.login.path}
            element={<FRONTEND_ROUTES.login.page />}
          />
          <Route
            path={FRONTEND_ROUTES.register.path}
            element={<FRONTEND_ROUTES.register.page />}
          />
          <Route
            path={FRONTEND_ROUTES.orders.path}
            element={<FRONTEND_ROUTES.orders.page />}
          />
          <Route
            path={FRONTEND_ROUTES.dashboard.path}
            element={<FRONTEND_ROUTES.dashboard.page />}
          />
          <Route
            path={FRONTEND_ROUTES.map.path}
            element={<FRONTEND_ROUTES.map.page />}
          />
          <Route
            path={FRONTEND_ROUTES.agvs.path}
            element={<FRONTEND_ROUTES.agvs.page />}
          />
          <Route
            path={FRONTEND_ROUTES.dashboardDemo.path}
            element={<FRONTEND_ROUTES.dashboardDemo.page />}
          />
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </BrowserRouter>
  );
}
