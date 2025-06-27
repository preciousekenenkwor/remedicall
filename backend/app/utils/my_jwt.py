from datetime import datetime, timedelta
from typing import Any

import jwt

from app.config import env

jwt_secret: str = env.env['jwt']["jwt_secret"]



class MyJwt:
    def __init__(
        self,
    ):
        self.JWT_SECRET: str = jwt_secret
        self.IAT = datetime.now()

    def create_token(self, subject: str,  token_type: str , expires_in: int):
        """
        This function creates a JWT token with specified subject, token type, and expiration time.
        
        :param subject: The `subject` parameter typically represents the entity to which the token is
        issued, such as a user ID or username. It helps identify the entity for which the token is generated
        :type subject: str
        :param token_type: The `token_type` parameter in the `create_token` function is used to specify the
        type of token being created. This could be a string indicating the purpose or nature of the token,
        such as "access_token", "refresh_token", "id_token", etc. It helps in identifying the token
        :type token_type: str
        :param expires_in: The `expires_in` parameter specifies the duration in minutes for which the token
        will be valid before it expires
        :type expires_in: int
        :return: The `create_token` method is returning a JWT token encoded with the payload containing the
        subject, token type, expiration time, issued at time, and algorithm information. The token is
        encoded using the `jwt.encode` method with the payload and a secret key (`self.JWT_SECRET`).
        """
        payload = {}
        expire = timedelta(minutes= expires_in)
        payload["exp"] = datetime.now() + expire
        payload["iat"] = datetime.now()
        payload["type"] = token_type
        payload["sub"] = subject
        payload["alg"] = "HS256"
# claims=payload, key=self.JWT_SECRET
        return jwt.encode(payload=payload, key=self.JWT_SECRET, algorithm="HS256")

    def verify_token(self, token: str) -> dict[str, Any]:
        """
        The function `verify_token` decodes a JWT token using a secret key and returns the decoded token as
        a dictionary.
        
        :param token: A JWT token that needs to be verified
        :type token: str
        :return: A dictionary containing the decoded token is being returned.
        """


        # token = token, key = self.JWT_SECRET
        decoded_token = jwt.decode(jwt=token, key=self.JWT_SECRET, algorithms=["RS256"])
        return decoded_token


