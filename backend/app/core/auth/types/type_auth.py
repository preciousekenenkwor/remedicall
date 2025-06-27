from typing import TypedDict


class ChangePassWordT(TypedDict):
    old_password:str
    new_password:str
    confirm_password:str
  


class VerifyResetTokenT(TypedDict):
    email: str
    token: str


# TypedDict definitions for all data structures
class CreateUserT(TypedDict):
    password: str
    email: str
    first_name: str
    last_name: str
    user_type: str


class LoginT(TypedDict):
    email: str
    password: str


class VerifyEmailT(TypedDict):
    email: str


class ForgotPasswordT(TypedDict):
    email: str


# The class `ResetPasswordT` is a TypedDict used for defining the structure of a dictionary for
# resetting passwords.
class ResetPasswordT(TypedDict):

    email: str
    token: str
    password: str


class ChangePasswordT(TypedDict):
    current_password: str
    new_password: str


class VerifyEmailTokenT(TypedDict):
    email: str
    token: str
