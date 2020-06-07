from common.enums.response_code import ResponseCode

def responseWrapper(response_code, data = None):
    return {
        'code': response_code.value[0],
        'msg': response_code.value[1],
        'data': data
    }

def errorWrapper(code, msg):
    return {
        'code': code,
        'msg': msg,
        'data': None
    }

def success(data = None):
    return responseWrapper(ResponseCode.OK, data)

def error(response_code):
    return responseWrapper(response_code)