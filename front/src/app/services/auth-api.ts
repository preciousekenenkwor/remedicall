/* eslint-disable @typescript-eslint/no-explicit-any */
import type { BaseAPI } from "./base-api";


export interface IToken{
    access: {
        token: string;
        expires: string;
    }
    refresh: {
        token: string;
        expires: string;
    }

}

export interface IUser{
    id: string;
    first_name: string;
    last_name: string;
    email: string;
    user_type: string;

    
}
export interface IAuthResponse{
    success: boolean;
    message: string;
    tokens: IToken;
    user: IUser
}

export interface ICreateUser{
    first_name: string;
    last_name: string;
    email: string;
    password: string;
    user_type: string;
}

export interface IVerifyEmail{
    email: string;
    token: string;
}

export class AuthApi {
    private baseApi: BaseAPI
    constructor(baseApi: BaseAPI) {
        this.baseApi = baseApi;
    }

    async signup(data: ICreateUser) {
        return this.baseApi.post<never, IAuthResponse>("/auth/register", data);
    }
    async login(data: Pick<ICreateUser, "email" | "password">) {
        return this.baseApi.post< IAuthResponse>("/auth/login", data);
    }

    async logout() {
        return this.baseApi.post<never, IAuthResponse>("/auth/logout",{});
    }
    async refreshToken() {
        return this.baseApi.post<never, IAuthResponse>("/auth/refresh-token", {});
    }
    async verifyEmail(data: IVerifyEmail) {
       
        return this.baseApi.post<never, IAuthResponse>("/auth/verify-email", data);
    }


    async verifyForgotPasswordToken(token: string, email: string) {
        return this.baseApi.post<string>("/auth/verify-reset-password", { token, email });
    }
    async resetPassword ({
        email,
        code,
        password
    }: {
        email: string;
        code: string;
        password: string;
 }) {
     return this.baseApi.post<never, IAuthResponse>("/auth/reset-password", { email, token:code, password });
 }
    verifyToken(token: string) {
        return this.baseApi.post<any>("/auth/verify-token", { token });
    }
    async forgotPassword(email: string) {
        return this.baseApi.post<string>(
          "/auth/forgot-password",
          { email }
        );
    }

    async resendVerificationEmail(email: string) {
        return this.baseApi.post<never, IAuthResponse>(
          "/auth/send-verification-email",
          { email }
        );
    }



}