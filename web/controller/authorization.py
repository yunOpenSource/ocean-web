import datetime

import jwt

from common.annotation.decorators import jsons, value
from common.enums.request_method import RequestMethod
from common.enums.response_code import ResponseCode
from common.response.response_wrapper import success
from common.run.container import route
from common.util.constant_util import JWT_HEADERS, JWT_ALGORITHM
from common.util.verify_util import equals, non_blank

@value(value = "${server.pre-path}", default_value="/api")
def prePath(): pass

@value(value = "${login.username}", default_value="xxx")
def loginUsername(): pass

@value(value = "${login.password}", default_value="xxx")
def loginPassword(): pass

@value(value = "${jwt.expiry}", default_value=30)
def jwtExpiry(): pass

@value(value = "${jwt.secret-key}", default_value="xxxx")
def jwtSecretKey(): pass

"""
用户登陆接口，需要登陆才可以访问其他接口
"""
@route(prePath() + "/v1/login", methods=[RequestMethod.POST.value])
@jsons({'username': {
   'verifies': [non_blank]
}, 'password': {
   'verifies': [non_blank]
}})
def authorization(username, password):
   equals(username, loginUsername(), ResponseCode.USERNAME_ERROR)
   equals(password, loginPassword(), ResponseCode.PASSWORD_ERROR)
   payload = {
      'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes=jwtExpiry())
   }
   return success({
      'token': jwt.encode(payload=payload, key=jwtSecretKey(), algorithm=JWT_ALGORITHM, headers=JWT_HEADERS).decode('utf8')
   })