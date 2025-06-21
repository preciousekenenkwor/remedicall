import { createSlice, type PayloadAction } from "@reduxjs/toolkit";
import type { modalI } from "./modal.interface";

const modalInitialState: modalI = {
  openDeleteModal: false,
  openInfoModal: false,
  openSomeModal: {},
};

const modalSlice = createSlice({
  name: "modal",
  initialState: modalInitialState,
  reducers: {
    openDeleteModal: (state) => {
      state.openDeleteModal = true;
    },
    closeDeleteModal: (state) => {
      state.openDeleteModal = false;
    },
    openInfoModal: (state) => {
      state.openInfoModal = true;
    },
    closeInfoModal: (state) => {
      state.openInfoModal = false;
    },
    openSomeModal: (state, action) => {
      if (!state.openSomeModal[action.payload]) {
        state.openSomeModal[action.payload] = {};
      }

      // Set the 'value' property to true
      state.openSomeModal[action.payload].value = true;
    },
    closeSomeModal: (state, action) => {
      // Set the 'value' property to true
      if (state.openSomeModal[action.payload]) {
        state.openSomeModal[action.payload].value = false;
        delete state.openSomeModal[action.payload];
      }
    },
    handleModalFunc: (
      state,
      action: PayloadAction<{ name: string; arrow: number }>
    ) => {
      // Set the 'value' property to true
      if (state.openSomeModal[action.payload.name]) {
        state.openSomeModal[action.payload.name].arrow = action.payload.arrow;
      }
    },
  },
});

export const {
  openDeleteModal,
  closeDeleteModal,
  closeInfoModal,
  openInfoModal,
  closeSomeModal,
  openSomeModal,
  handleModalFunc,
} = modalSlice.actions;
export const modalReducer = modalSlice.reducer;
