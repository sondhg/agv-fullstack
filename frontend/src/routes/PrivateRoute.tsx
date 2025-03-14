import { useAuth } from "@/hooks/useAuth";
import { Navigate, Outlet } from "react-router-dom";

export function PrivateRoute() {
  const { isAuthenticated } = useAuth();

  if (!isAuthenticated) {
    return <Navigate to="/login" />; //ko dùng useNavigate, sẽ lỗi
  }
  // return <>{props.children}</>;
  return <Outlet />;
}
