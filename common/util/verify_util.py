from common.exception.business_exception import BusinessException


def equals(objA, objB, response_code):
    if objA != objB:
        raise BusinessException(response_code, None)


def non_blank(param, response_code):
    if param == None or len(param) == 0:
        raise BusinessException(response_code, None)