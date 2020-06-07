from common.enums.response_code import ResponseCode
from common.exception.business_exception import BusinessException
from common.response.response_wrapper import error, errorWrapper
from common.run.container import errorhandler

@errorhandler(BusinessException)
def business_exception_handler(e):
    return error(e.responseCode())

@errorhandler(Exception)
def exception_handler(e):
    return errorWrapper(ResponseCode.SERVER_ERROR.value[0], str(e))