

export class AppConfig {
  public static readonly API_URL = "http://localhost:8000";
  public static readonly API_VERSION = "/api/v1";
  public static readonly BASE_URL = AppConfig.API_URL + AppConfig.API_VERSION;
    public static readonly USER_KEY = "user";
    public static TOKEN_KEY = "token";
  public static RESET_EMAIL_KEY = "reset_email";
  public static RESET_TOKEN_KEY = "reset_token";
    
  public static EXPIRE_KEY = "token_expiry_time";
  public static REFRESH_TOKEN_KEY = "refresh_token";
  public static REFRESH_EXPIRE_KEY = "refresh_token_expiry_time";
}

