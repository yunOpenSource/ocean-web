from enum import Enum


class ResponseCode(Enum):
    OK = (0, "success")
    SERVER_ERROR = (50000, "Server Error")
    PARAM_ERROR = (40000, "Param Error")
    AUTH_ERROR = (40003, "No Authorization")
    USERNAME_ERROR = (40001, "Username Error")
    PASSWORD_ERROR = (40001, "Password Error")