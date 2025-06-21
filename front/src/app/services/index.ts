import { AuthApi } from "./auth-api";
import { BaseAPI } from "./base-api";

import { UtilityApi } from "./utility";



export class MediguardApi{
    public baseApi: BaseAPI


    public utilityApi: UtilityApi
    public authApi: AuthApi
    constructor (
        isAuthRoute: boolean = true,
        useMultiPartFormData: boolean = false,
        useAxios: boolean = true
    ) {
        this.baseApi = new BaseAPI(isAuthRoute, useMultiPartFormData, useAxios);
        this.utilityApi = new UtilityApi(this.baseApi)
        this.authApi = new AuthApi(this.baseApi)
}


    

}