import { createSlice, PayloadAction } from "@reduxjs/toolkit";

interface AccountState {
  access_token: string;
  refresh_token: string;
  name: string;
  email: string;
}

interface UserState {
  account: AccountState;
  isAuthenticated: boolean;
}

const initialState: UserState = {
  account: {
    access_token: "",
    refresh_token: "",
    name: "",
    email: "",
  },
  isAuthenticated: false,
};

const userSlice = createSlice({
  name: "user",
  initialState,
  reducers: {
    doLogin(state, action: PayloadAction<AccountState>) {
      state.account = action.payload;
      state.isAuthenticated = true;
    },
    doLogout(state) {
      state.account = {
        access_token: "",
        refresh_token: "",
        name: "",
        email: "",
      };
      state.isAuthenticated = false;
    },
  },
});

export const { doLogin, doLogout } = userSlice.actions;
export default userSlice.reducer;
