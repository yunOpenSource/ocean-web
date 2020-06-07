import threading
import time

from common.annotation.decorators import jsons, args, form, auth, thread_local
from common.enums.request_method import RequestMethod
from common.response.response_wrapper import success
from common.run.container import route, logger
from common.util.verify_util import non_blank
from web.service.hello_service import hello


@route("/", methods=[RequestMethod.POST.value])
@auth()
# @jsons({'name': {'verifies': [non_blank]}})
# @args({'name': {'verifies': [non_blank]}})
@form({'name': {'verifies': [non_blank]}})
def home(name, age = None):
    logger.info(threading.currentThread().ident)
    hello()
    return success({
        'name': name,
        'age': age
    })

@route("/test/<id>", methods=[RequestMethod.GET.value])
@args({'name': {'verifies': [non_blank]}})
def test(id, name):
    logger.info(threading.currentThread().ident)
    time.sleep(10)
    logger.info("haha %s" % thread_local.id)
    return success({
        'name': name,
        'id': id
    })
