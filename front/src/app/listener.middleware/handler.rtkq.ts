import { updateOnlineStatus } from "../slices/utils/utils.slices";
import { AppDispatch } from "../store";

interface Params {
  dispatch: AppDispatch;
  operation: string;
}

export default async function RTKQHandler({ dispatch, operation }: Params) {
  switch (operation) {
    case "offline":
      {
        dispatch(updateOnlineStatus(false));
      }
      break;
    case "online":
      {
        dispatch(updateOnlineStatus(true));
      }
      break;
    default:
      break;
  }
}
