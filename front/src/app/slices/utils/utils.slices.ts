import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { UtilsSliceType } from "./utils.types";


const initialState: UtilsSliceType = {
  isOnline: true,
  serverStatus: "disconnected",
  isReady: false,
};

const utilsSlice = createSlice({
  initialState,
  name: "utils",
  reducers: {
    updateUtils: (state, action: PayloadAction<UtilsSliceType>) => {
      const { isOnline, serverStatus, ...paylaod } = action.payload;

      return { ...state, ...paylaod, isOnline, serverStatus };
    },
    updateOnlineStatus(state, action: PayloadAction<boolean>) {
      //console.log(action.payload, "---------------->>>>>");
      state.isOnline = action.payload;
    },
  },
});

export const { updateOnlineStatus, updateUtils } = utilsSlice.actions;
export const utilsReducer = utilsSlice.reducer;
