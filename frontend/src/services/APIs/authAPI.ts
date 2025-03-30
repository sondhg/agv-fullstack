import {
  CreateLoginDto,
  CreateLogoutDto,
  CreateRegisterDto,
  LoginResponse,
  LogoutResponse,
  RegisterResponse,
} from "@/types/Auth.types";
import { apiService } from "./apiService";
import { API_ENDPOINTS } from "./apiEndpoints";

const postLogin = async (loginInfo: CreateLoginDto): Promise<LoginResponse> => {
  return apiService.post(API_ENDPOINTS.auth.login, loginInfo);
};

const postRegister = async (
  registerInfo: CreateRegisterDto,
): Promise<RegisterResponse> => {
  return apiService.post(API_ENDPOINTS.auth.register, registerInfo);
};

const postLogout = async (
  logoutInfo: CreateLogoutDto,
): Promise<LogoutResponse> => {
  return apiService.post(API_ENDPOINTS.auth.logout, logoutInfo);
};

export { postLogin, postLogout, postRegister };
