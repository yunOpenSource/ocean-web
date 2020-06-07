from enum import Enum


class RequestHeader(Enum):
    AUTH = "X-Authorization"
    LANGUAGE = "X-Language"