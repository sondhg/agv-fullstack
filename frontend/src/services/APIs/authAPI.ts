import {
  CreateLoginDto,
  CreateLogoutDto,
  CreateRegisterDto,
  LoginResponse,
  LogoutResponse,
  RegisterResponse,
} from "@/types/Auth.types";
import api from "@/utils/axiosCustomize";
import { AxiosError } from "axios";

const LOGIN_URL = "login";
const REGISTER_URL = "register";
const LOGOUT_URL = "logout";

const postLogin = async (loginInfo: CreateLoginDto): Promise<LoginResponse> => {
  try {
    const { data } = await api.post(LOGIN_URL, loginInfo);
    return data;
  } catch (error) {
    const err = error as AxiosError; // Type assertion
    interface ErrorResponse {
      detail?: string;
    }
    const errorData = err.response?.data as ErrorResponse;
    const errorMessage = errorData?.detail || "Failed to log in";
    console.log(">>> Error logging in:", errorMessage);
    throw new Error(errorMessage);
  }
};

const postRegister = async (
  registerInfo: CreateRegisterDto,
): Promise<RegisterResponse> => {
  try {
    const { data } = await api.post(REGISTER_URL, registerInfo);
    return data;
  } catch (error) {
    console.log(">>> Full error object:", error);
    const err = error as AxiosError; // Type assertion
    interface ErrorResponse {
      email?: string;
      name?: string;
    }
    const errorData = err.response?.data as ErrorResponse;
    const errorMessageRegisteredEmail = errorData?.email;
    const errorMessageRegisteredName = errorData?.name;
    let errorMessage: string = "Failed to register";
    if (errorMessageRegisteredName) {
      errorMessage = errorMessageRegisteredName;
    } else if (errorMessageRegisteredEmail) {
      errorMessage = errorMessageRegisteredEmail;
    }
    throw new Error(errorMessage);
  }
};

const postLogout = async (
  logoutInfo: CreateLogoutDto,
): Promise<LogoutResponse> => {
  try {
    const { data } = await api.post(LOGOUT_URL, logoutInfo);
    return data;
  } catch (error) {
    console.error(">>> Error logging out:", error);
    throw new Error(">>> Failed to log out");
  }
};

export { postLogin, postLogout, postRegister };

