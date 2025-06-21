/* eslint-disable @typescript-eslint/no-explicit-any */
import clearTable from "./clear.handler";

interface Params {
  data: any;
  operation: string;
}
export async function utilsHandler({ operation, data = {} }: Params) {
  const table = window.CACHE["utils"];
  if (operation.startsWith("reset")) {
    clearTable("utils");
    return;
  }
  switch (operation) {
    case "toggleMenuExpand":
      {
        // //console.log("cache the toggleMenuExpand");
        await table?.setItem("menuExpand", data.menuExpand);
      }
      break;
    case "updateInputMode":
      {
        await table?.setItem("inputMode", data.inputMode);
      }
      break;
    case "updateFileListView":
      {
        await table?.setItem("fileListView", data.fileListView);
      }
      break;
    default:
      break;
  }
}
