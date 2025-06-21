export interface modalI {
  openDeleteModal: boolean;
  openInfoModal: boolean;

  openSomeModal: {
    [key: string]: { value?: boolean,arrow?:number };
  };
}
