/* eslint-disable @typescript-eslint/no-explicit-any */
import { createListenerMiddleware } from "@reduxjs/toolkit";
import { RootState } from "../store";
import RTKQHandler from "./handler.rtkq";
import { utilsHandler } from "./handler.utils";
const operations = ["__rtkq", "utils"];
const listener = createListenerMiddleware();

listener.startListening({
  predicate: (action) => {
    const { type = "" } = action;

    if (!type || !String(type).includes("/")) return false;

    const [prefix] = type.split("/");
    return operations.includes(prefix);
  },
  effect: async (action, listenerApi) => {
    const { type = "" /* payload */ } = action;

    const [prefix, operation]: [keyof RootState | "__rtkq", string] =
      type.split("/") as [keyof RootState | "__rtkq", string];
    if (!window.CACHE && prefix !== "__rtkq") return;
    const currentState = listenerApi.getState() as RootState;
    const state = prefix == "__rtkq" ? null : currentState[prefix];
    switch (prefix) {
      case "__rtkq":
        {
          await RTKQHandler({
            operation,

            dispatch: listenerApi.dispatch as any,
          });
        }

        break;
      case "utils":
        {
          await utilsHandler({ data: state, operation });
        }
        break;
      default:
        break;
    }
  },
});

export default listener;
