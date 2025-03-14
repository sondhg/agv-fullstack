import { useSelector } from "react-redux";
import { RootState } from "@/redux/store";

export const useAuth = () => {
  const account = useSelector((state: RootState) => state.user.account);
  const isAuthenticated = useSelector(
    (state: RootState) => state.user.isAuthenticated,
  );

  return { account, isAuthenticated };
};
