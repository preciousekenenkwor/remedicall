import { BaseAPI } from "./base-api";

export class UtilityApi{
    private baseApi: BaseAPI;
   
     constructor(baseApi: BaseAPI) {
       this.baseApi = baseApi;
     }
     
    
  // Utility method to manually refresh tokens
  async forceRefreshTokens(): Promise<void> {
    await this.baseApi.refreshTokens();
  }

  // Utility method to check if user is authenticated
  async isAuthenticated(): Promise<boolean> {
    const tokens = await this.baseApi.getStoredTokens();
    return tokens !== null && !this.baseApi.isTokenExpired(tokens.refresh.expires);
  }

  // Utility method to get current user token info
  async getTokenInfo(): Promise<{
    hasTokens: boolean;
    accessExpired: boolean;
    refreshExpired: boolean;
  } | null> {
    const tokens = await this.baseApi.getStoredTokens();
    if (!tokens) return null;

    return {
      hasTokens: true,
      accessExpired: this.baseApi.isTokenExpired(tokens.access.expires),
      refreshExpired: this.baseApi.isTokenExpired(tokens.refresh.expires),
    };
  }
}