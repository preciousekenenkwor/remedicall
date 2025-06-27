from typing import TypedDict

from pydantic_settings import BaseSettings, SettingsConfigDict


class Mail_Env_Type(TypedDict):
    mail_server:str
    mail_port:int
    mail_username:str
    mail_password:str
    use_credentials:bool
    mail_use_ssl:bool
    mail_use_tls:bool
    mail_sender:str
    mail_sender_name:str
    use_mail_service:bool




    
  
class JWT_Env_Type(TypedDict):
    jwt_secret: str
    jwt_access_expiry_time:int
    jwt_refresh_expiry_time: int
    jwt_expiry_time:str
class env_type(TypedDict):
    jwt:JWT_Env_Type
    env_type:str
 
    database_url:str
    mail:Mail_Env_Type
  
    
  


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", validate_default=False)
    jwt_secret: str=""
    jwt_access_expiry_time:str=""
    jwt_refresh_expiry_time: str=""
    jwt_expiry_time:str=""
    database_url:str=""
    mail_server:str=''
    mail_port:int =0
    mail_username:str=''
    mail_password:str=''
    use_credentials:bool=False
    mail_use_ssl:bool=False
    mail_use_tls:bool=False
    mail_sender:str=''
    mail_sender_name:str=""
    env_type: str=''
    use_mail_service:bool=False

    

    
    





# @lru_cache
settings:Settings = Settings()

env:env_type = {"database_url":settings.database_url, "env_type":settings.env_type,
                "jwt":{
                "jwt_expiry_time":settings.jwt_expiry_time, 
                "jwt_secret":settings.jwt_secret,  
                "jwt_access_expiry_time":int(settings.jwt_access_expiry_time),
                "jwt_refresh_expiry_time":int(settings.jwt_refresh_expiry_time)},
                "mail":{
                    "mail_password":settings.mail_password,
                    "mail_port":settings.mail_port,
                    "mail_server":settings.mail_server,
                    "mail_sender":settings.mail_sender,
                    "mail_use_tls":settings.mail_use_tls,
                    "mail_use_ssl":settings.mail_use_ssl,
                    "mail_username":settings.mail_username,
                    "use_credentials":settings.use_credentials,
                    "mail_sender_name":settings.mail_sender_name,
                    
                    "use_mail_service": settings.use_mail_service
                    
                },
             
                 }
