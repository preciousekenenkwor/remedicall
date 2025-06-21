export interface UtilsSliceType {
  isOnline: boolean;
  serverStatus: SSEStatus;
  isReady: boolean;
}
export type SSEStatus =
  | "connecting"
  | "connected"
  | "disconnected"
  | "reconnecting";
