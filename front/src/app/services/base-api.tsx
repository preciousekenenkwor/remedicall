/* eslint-disable @typescript-eslint/no-unused-vars */
/* eslint-disable @typescript-eslint/no-explicit-any */
 

import { AppConfig } from "@/app/config";
import { staticToast } from "@/utils/toaster";

import axios, { AxiosError, type AxiosInstance, type AxiosResponse } from "axios";
import type { IUser } from "./auth-api";

export interface ISuccessResponse<T> {
  success: boolean;
  message: string;
  data: T;
  doc_length?: number;
}

export interface IErrorResponse {
  error: any;
  success: boolean;
  message: string;
}

export interface AuthTokens {
  access: { token: string; expires: string };
  refresh: { token: string; expires: string };
}

export interface RefreshTokenResponse {
  tokens: AuthTokens;
}

export class BaseAPI {
  private baseURL: string;
  private isAuthRoute: boolean;
  private useMultiPartFormData: boolean;
  private useAxios: boolean;
  private axiosInstance?: AxiosInstance;
  private isRefreshing: boolean = false;
  private failedQueue: Array<{
    resolve: (token: string) => void;
    reject: (error: any) => void;
  }> = [];

  constructor(
    isAuthRoute: boolean = true,
    useMultiPartFormData: boolean = false,
    useAxios: boolean = true
  ) {
    this.useMultiPartFormData = useMultiPartFormData;
    this.baseURL = AppConfig.BASE_URL;
    this.isAuthRoute = isAuthRoute;
    this.useAxios = useAxios;

    if (this.useAxios) {
      this.initializeAxios();
    }
  }

  private isFormData(data: any): boolean {
    return data instanceof FormData;
  }

  // Token management methods
  public async getStoredTokens(): Promise<AuthTokens | null> {
    try {
      const accessToken = localStorage.getItem(AppConfig.TOKEN_KEY);
      const refreshToken = localStorage.getItem(AppConfig.REFRESH_TOKEN_KEY);
      const accessExpires = localStorage.getItem(AppConfig.EXPIRE_KEY);
      const refreshExpires = localStorage.getItem(AppConfig.REFRESH_EXPIRE_KEY);

      if (accessToken && refreshToken && accessExpires && refreshExpires) {
        return {
          access: { token: accessToken, expires: accessExpires },
          refresh: { token: refreshToken, expires: refreshExpires },
        };
      }
    } catch (error) {
      console.error("Error getting stored tokens:", error);
    }
    return null;
  }

  public async storeTokens(tokens: AuthTokens): Promise<void> {
    try {
      localStorage.setItem(AppConfig.TOKEN_KEY, tokens.access.token);
      localStorage.setItem(AppConfig.REFRESH_TOKEN_KEY, tokens.refresh.token);
      localStorage.setItem(AppConfig.EXPIRE_KEY, tokens.access.expires);
      localStorage.setItem(
        AppConfig.REFRESH_EXPIRE_KEY,
        tokens.refresh.expires
      );
    } catch (error) {
      console.error("Error storing tokens:", error);
    }
  }
public async storeUser(user: IUser): Promise<void> {
  try {
    localStorage.setItem(AppConfig.USER_KEY, JSON.stringify(user));
  } catch (error) {
    console.error('Error saving user:', error);
  }
}
  public async clearUser(): Promise<void> {
    try {
      localStorage.removeItem(AppConfig.USER_KEY);
    } catch (error) {
      console.error('Error clearing user:', error);
    }
  }
  public async getUser(): Promise<IUser | null> {
    try {
      const userJson = localStorage.getItem(AppConfig.USER_KEY);
      if (userJson) {
        return JSON.parse(userJson) as IUser;
      }
    } catch (error) {
      console.error('Error getting user:', error);
    }
    return null;
  }

  private async clearTokens(): Promise<void> {
    try {
      localStorage.removeItem(AppConfig.TOKEN_KEY);
      localStorage.removeItem(AppConfig.REFRESH_TOKEN_KEY);
      localStorage.removeItem(AppConfig.EXPIRE_KEY);
      localStorage.removeItem(AppConfig.REFRESH_EXPIRE_KEY);
    } catch (error) {
      console.error("Error clearing tokens:", error);
    }
  }

  public isTokenExpired(expires: string): boolean {
    try {
      const expirationTime = new Date(expires).getTime();
      const currentTime = Date.now();
      // Add 5 minute buffer before expiration
      return expirationTime - currentTime < 5 * 60 * 1000;
    } catch (error) {
      console.error("Error checking token expiration:", error);
      return true;
    }
  }

  public async refreshTokens(): Promise<string> {
    if (this.isRefreshing) {
      // If already refreshing, wait for it to complete
      return new Promise((resolve, reject) => {
        this.failedQueue.push({ resolve, reject });
      });
    }

    this.isRefreshing = true;

    try {
      const tokens = await this.getStoredTokens();
      if (!tokens?.refresh.token) {
        throw new Error("No refresh token available");
      }

      // Check if refresh token is expired
      if (this.isTokenExpired(tokens.refresh.expires)) {
        throw new Error("Refresh token expired");
      }

      const response = await fetch(
        `${this.baseURL}/api/v1/auth/refresh-tokens`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${tokens.refresh.token}`,
          },
          body: JSON.stringify({ refreshToken: tokens.refresh.token }),
        }
      );

      if (!response.ok) {
        throw new Error("Token refresh failed");
      }

      const data: RefreshTokenResponse = await response.json();
      await this.storeTokens(data.tokens);

      // Process failed queue
      this.failedQueue.forEach(({ resolve }) => {
        resolve(data.tokens.access.token);
      });
      this.failedQueue = [];

      return data.tokens.access.token;
    } catch (error) {
      // Process failed queue with error
      this.failedQueue.forEach(({ reject }) => {
        reject(error);
      });
      this.failedQueue = [];

      // Clear tokens and redirect to login
      await this.clearTokens();
      staticToast.error("Session expired. Please log in again.");

      // Redirect to login - you might want to use your router here
      if (typeof window !== "undefined") {
        window.location.href = "/auth/login";
      }

      throw error;
    } finally {
      this.isRefreshing = false;
    }
  }

  private async getValidAccessToken(): Promise<string | null> {
    if (!this.isAuthRoute) return null;

    const tokens = await this.getStoredTokens();
    if (!tokens?.access.token) return null;

    // Check if token needs refresh
    if (this.isTokenExpired(tokens.access.expires)) {
      try {
        return await this.refreshTokens();
      } catch (error) {
        console.error("Token refresh failed:", error);
        return null;
      }
    }

    return tokens.access.token;
  }

  private initializeAxios(): void {
    this.axiosInstance = axios.create({
      baseURL: this.baseURL,
      timeout: 30000, // 30 seconds timeout
      withCredentials: true,
    });

    this.axiosInstance.interceptors.request.use(
      async (config) => {
        try {
          // Check if data is FormData
          const isFormData = this.isFormData(config.data);

          // Set content type - let axios handle FormData boundary automatically
          if (!isFormData && !this.useMultiPartFormData) {
            config.headers.set("Content-Type", "application/json");
          } else if (isFormData) {
            // Remove Content-Type header for FormData - let axios set it with boundary
            config.headers.delete("Content-Type");
          } else if (this.useMultiPartFormData && !isFormData) {
            // If flag is set but data isn't FormData, set multipart header
            config.headers.set("Content-Type", "multipart/form-data");
          }

          config.headers.set("Accept", "application/json");

          // Add auth header if needed
          if (this.isAuthRoute) {
            const token = await this.getValidAccessToken();
            if (token) {
              config.headers.set("Authorization", `Bearer ${token}`);
            } else {
              console.warn("No valid token available for authorization");
            }
          }

          return config;
        } catch (error) {
          console.error("Request interceptor error:", error);
          return config;
        }
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor to handle errors and token refresh
    this.axiosInstance.interceptors.response.use(
      (response: AxiosResponse) => {
        return response;
      },
      async (error: AxiosError) => {
        const originalRequest = error.config as any;

        // Handle 401 errors with token refresh
        if (
          error.response?.status === 401 &&
          !originalRequest._retry &&
          this.isAuthRoute
        ) {
          originalRequest._retry = true;

          try {
            const newToken = await this.refreshTokens();
            if (newToken && originalRequest.headers) {
              originalRequest.headers.Authorization = `Bearer ${newToken}`;
              return this.axiosInstance!.request(originalRequest);
            }
          } catch (refreshError) {
            console.error("Token refresh failed:", refreshError);
            // Error handling is done in refreshTokens method
          }
        }

        this.handleAxiosError(error);
        return Promise.reject(error.response?.data || error);
      }
    );
  }

  private handleAxiosError(error: AxiosError): void {
    const errorData = error.response as any;
    const status = error.response?.status;

    console.error("Axios API Error:", { error, status, data: errorData });

    // Special handling for 401 Unauthorized errors
    if (status === 401) {
      // Token refresh logic is handled in the response interceptor
      // Only show this message if refresh also failed
      if (!this.isRefreshing) {
        staticToast.error(
          "You are not logged in or your session has expired. Please log in again."
        );
      }
    } else {
      // Display toast notification for other errors
      const errorMessage = this.formatErrorMessage(
        errorData || {
          error: error.message,
          status: status?.toString() || "0",
          code: error.code || "NETWORK_ERROR",
          description: "Network request failed",
          traceId: "",
        }
      );
      staticToast.error(errorMessage);
    }
  }

  private async getHeaders(data?: any): Promise<HeadersInit> {
    const isFormData = this.isFormData(data);

    const headers: HeadersInit = {
      Accept: "application/json",
    };

    // Don't set Content-Type for FormData - let fetch handle it
    if (!isFormData && !this.useMultiPartFormData) {
      headers["Content-Type"] = "application/json";
    } else if (this.useMultiPartFormData && !isFormData) {
      headers["Content-Type"] = "multipart/form-data";
    }

    if (this.isAuthRoute) {
      const token = await this.getValidAccessToken();
      if (token) {
        headers["Authorization"] = `Bearer ${token}`;
      }
    }

    return headers;
  }

  private formatErrorMessage(errorData: any): string {
    // Handle auth errors
    if (errorData.code === "auth/unauthorized") {
      return "You are not logged in or your session has expired. Please log in again.";
    }

    // Handle validation errors with details
    if (errorData.detail && typeof errorData.detail === "object") {
      // Collect all error messages from the detail object
      const errorMessages: string[] = [];
      Object.entries(errorData.detail).forEach(([_field, messages]) => {
        if (Array.isArray(messages)) {
          messages.forEach((message) => {
            errorMessages.push(message);
          });
        }
      });

      if (errorMessages.length > 0) {
        return errorMessages.join(". ");
      }
    }

    // Default error message when no detail is available
    return (
      errorData.error ||
      errorData.description ||
      "An error occurred. Please try again."
    );
  }

  private async handleResponse<T, U = ISuccessResponse<T>>(
    response: Response
  ): Promise<U> {
    if (!response.ok) {
      let errorData: any;

      try {
        const clonedResponse = response.clone();
        errorData = await clonedResponse.json();
      } catch (e) {
        errorData = {
          error: "Request failed",
          status: response.status.toString(),
          code: "FETCH_ERROR",
          description: response.statusText,
          traceId: "",
        };
      }

      console.error("API Error:", {
        status: response.status,
        data: errorData,
      });

      // Handle 401 errors with token refresh for fetch requests
      if (response.status === 401 && this.isAuthRoute) {
        try {
          await this.refreshTokens();
          // Don't throw here, let the calling method retry
          throw { shouldRetry: true, ...errorData };
        } catch (refreshError) {
          console.error("Token refresh failed:", refreshError);
        }
      } else {
        const errorMessage = this.formatErrorMessage(errorData);
        staticToast.error(errorMessage);
      }

      throw errorData;
    }

    try {
      const clonedResponse = response.clone();
      return await clonedResponse.json();
    } catch (error) {
      console.error("JSON parsing error:", error);
      staticToast.error("Failed to parse server response");

      throw {
        error: "Invalid JSON response",
        status: "500",
        code: "JSON_PARSE_ERROR",
        description: "Failed to parse server response",
        traceId: "",
      };
    }
  }

  // Helper method to retry fetch requests
  private async retryWithNewToken<T, U = ISuccessResponse<T>>(
    url: string,
    options: RequestInit
  ): Promise<U> {
    const token = await this.getValidAccessToken();
    if (token && options.headers) {
      (options.headers as any)["Authorization"] = `Bearer ${token}`;
    }

    const response = await fetch(`${this.baseURL}${url}`, options);
    return await this.handleResponse<T, U>(response);
  }

  // Axios-based methods
  private async axiosGet<T, U = ISuccessResponse<T>>(url: string): Promise<U> {
    if (!this.axiosInstance) {
      throw new Error("Axios instance not initialized");
    }

    const response = await this.axiosInstance.get<U>(url);
    return response.data;
  }

  private async axiosPost<T, U = ISuccessResponse<T>>(
    url: string,
    data: any
  ): Promise<U> {
    if (!this.axiosInstance) {
      throw new Error("Axios instance not initialized");
    }

    const response = await this.axiosInstance.post<U>(url, data);
    return response.data;
  }

  private async axiosPut<T, U = ISuccessResponse<T>>(
    url: string,
    data: any
  ): Promise<U> {
    if (!this.axiosInstance) {
      throw new Error("Axios instance not initialized");
    }

    const response = await this.axiosInstance.put<U>(url, data);
    return response.data;
  }

  private async axiosPatch<T, U = ISuccessResponse<T>>(
    url: string,
    data: any
  ): Promise<U> {
    if (!this.axiosInstance) {
      throw new Error("Axios instance not initialized");
    }

    const response = await this.axiosInstance.patch<U>(url, data);
    return response.data;
  }

  private async axiosDelete<T, U = ISuccessResponse<T>>(
    url: string
  ): Promise<U> {
    if (!this.axiosInstance) {
      throw new Error("Axios instance not initialized");
    }

    const response = await this.axiosInstance.delete<U>(url);
    return response.data;
  }

  // Public API methods that choose between fetch and axios
  async get<T, U = ISuccessResponse<T>>(url: string): Promise<U> {
    try {
      if (this.useAxios) {
        return await this.axiosGet<T, U>(url);
      } else {
        const options: RequestInit = {
          method: "GET",
          headers: await this.getHeaders(),
          credentials: "include",
        };

        try {
          const response = await fetch(`${this.baseURL}${url}`, options);
          return await this.handleResponse<T, U>(response);
        } catch (error: any) {
          if (error.shouldRetry) {
            return await this.retryWithNewToken<T, U>(url, options);
          }
          throw error;
        }
      }
    } catch (error) {
      console.error("Get request error:", error);
      throw error;
    }
  }

  async post<T, U = ISuccessResponse<T>>(url: string, data: any): Promise<U> {
    try {
      if (this.useAxios) {
        return await this.axiosPost<T, U>(url, data);
      } else {
        const isFormData = this.isFormData(data);
        const options: RequestInit = {
          method: "POST",
          headers: await this.getHeaders(data),
          body:
            isFormData || this.useMultiPartFormData
              ? data
              : JSON.stringify(data),
          credentials: "include",
        };

        try {
          const response = await fetch(`${this.baseURL}${url}`, options);
          return await this.handleResponse<T, U>(response);
        } catch (error: any) {
          if (error.shouldRetry) {
            return await this.retryWithNewToken<T, U>(url, options);
          }
          throw error;
        }
      }
    } catch (error) {
      console.error("Post request error:", error);
      throw error;
    }
  }

  async put<T, U = ISuccessResponse<T>>(url: string, data: any): Promise<U> {
    try {
      if (this.useAxios) {
        return await this.axiosPut<T, U>(url, data);
      } else {
        const isFormData = this.isFormData(data);
        const options: RequestInit = {
          method: "PUT",
          headers: await this.getHeaders(data),
          body: isFormData ? data : JSON.stringify(data),
          credentials: "include",
        };

        try {
          const response = await fetch(`${this.baseURL}${url}`, options);
          return await this.handleResponse<T, U>(response);
        } catch (error: any) {
          if (error.shouldRetry) {
            return await this.retryWithNewToken<T, U>(url, options);
          }
          throw error;
        }
      }
    } catch (error) {
      console.error("Put request error:", error);
      throw error;
    }
  }

  async patch<T, U = ISuccessResponse<T>>(url: string, data: any): Promise<U> {
    try {
      if (this.useAxios) {
        return await this.axiosPatch<T, U>(url, data);
      } else {
        const isFormData = this.isFormData(data);
        const options: RequestInit = {
          method: "PATCH",
          headers: await this.getHeaders(data),
          body: isFormData ? data : JSON.stringify(data),
          credentials: "include",
        };

        try {
          const response = await fetch(`${this.baseURL}${url}`, options);
          return await this.handleResponse<T, U>(response);
        } catch (error: any) {
          if (error.shouldRetry) {
            return await this.retryWithNewToken<T, U>(url, options);
          }
          throw error;
        }
      }
    } catch (error) {
      console.error("Patch request error:", error);
      throw error;
    }
  }

  async delete<T, U = ISuccessResponse<T>>(url: string): Promise<U> {
    try {
      if (this.useAxios) {
        return await this.axiosDelete<T, U>(url);
      } else {
        const options: RequestInit = {
          method: "DELETE",
          headers: await this.getHeaders(),
          credentials: "include",
        };

        try {
          const response = await fetch(`${this.baseURL}${url}`, options);
          return await this.handleResponse<T, U>(response);
        } catch (error: any) {
          if (error.shouldRetry) {
            return await this.retryWithNewToken<T, U>(url, options);
          }
          throw error;
        }
      }
    } catch (error) {
      console.error("Delete request error:", error);
      throw error;
    }
  }

  // Convenience methods for FormData
  async postForm<T, U = ISuccessResponse<T>>(
    url: string,
    data: FormData
  ): Promise<U> {
    if (this.useAxios && this.axiosInstance) {
      const response = await this.axiosInstance.postForm<U>(url, data);
      return response.data;
    } else {
      const options: RequestInit = {
        method: "POST",
        headers: await this.getHeaders(data),
        body: data,
        credentials: "include",
      };

      try {
        const response = await fetch(`${this.baseURL}${url}`, options);
        return await this.handleResponse<T, U>(response);
      } catch (error: any) {
        if (error.shouldRetry) {
          return await this.retryWithNewToken<T, U>(url, options);
        }
        throw error;
      }
    }
  }

  async putForm<T, U = ISuccessResponse<T>>(
    url: string,
    data: FormData
  ): Promise<U> {
    if (this.useAxios && this.axiosInstance) {
      const response = await this.axiosInstance.putForm<U>(url, data);
      return response.data;
    } else {
      const options: RequestInit = {
        method: "PUT",
        headers: await this.getHeaders(data),
        body: data,
        credentials: "include",
      };

      try {
        const response = await fetch(`${this.baseURL}${url}`, options);
        return await this.handleResponse<T, U>(response);
      } catch (error: any) {
        if (error.shouldRetry) {
          return await this.retryWithNewToken<T, U>(url, options);
        }
        throw error;
      }
    }
  }

  async patchForm<T, U = ISuccessResponse<T>>(
    url: string,
    data: FormData
  ): Promise<U> {
    if (this.useAxios && this.axiosInstance) {
      const response = await this.axiosInstance.patchForm<U>(url, data);
      return response.data;
    } else {
      const options: RequestInit = {
        method: "PATCH",
        headers: await this.getHeaders(data),
        body: data,
        credentials: "include",
      };

      try {
        const response = await fetch(`${this.baseURL}${url}`, options);
        return await this.handleResponse<T, U>(response);
      } catch (error: any) {
        if (error.shouldRetry) {
          return await this.retryWithNewToken<T, U>(url, options);
        }
        throw error;
      }
    }
  }
}
