// src/store/store.ts
// import { TypedUseSelectorHook, useDispatch, useSelector } from "react-redux";

import { combineReducers, configureStore } from "@reduxjs/toolkit";
import { setupListeners } from "@reduxjs/toolkit/query";
import { modalReducer } from "./slices/modal/modal.types";
import { utilsReducer } from "./slices/utils/utils.slices";


const reducer = combineReducers({
  

  utils: utilsReducer,
  modal:modalReducer
});

// Configure the store
const store = configureStore({
  reducer,
  middleware: (getDefaultMiddleware) => getDefaultMiddleware()
    .concat(
     
     

      )


});

let initialized = false;
setupListeners(store.dispatch, (dispatch, { onOnline, onOffline }) => {
  const handleOnline = () => dispatch(onOnline());
  const handleOffline = () => dispatch(onOffline());
  if (!initialized) {
    if (typeof window !== "undefined" && window.addEventListener) {
      // Handle connection events
      window.addEventListener("online", handleOnline, false);
      window.addEventListener("offline", handleOffline, false);
      initialized = true;
    }
  }

  return () => {
    window.removeEventListener("online", handleOnline);
    window.removeEventListener("offline", handleOffline);
    initialized = false;
  };
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;

export default store;