import threading

import jwt
from flask import request

from common.enums.request_header import RequestHeader
from common.enums.response_code import ResponseCode
from common.exception.business_exception import BusinessException
from common.run.container import Container, logger
from common.util.constant_util import JWT_OPTIONS
from common.util.string_util import matchReplace, PATTERN_NAME, matchParams, PATTERN_PARAMS

"""
线程共享变量
"""
thread_local = threading.local()

"""
注解实现单例模式
"""
def singleton(clazz):
    instances = {}

    def getInstance(*args, **kwargs):
        key = (clazz, args)
        if key not in instances:
            instances[key] = clazz(*args, **kwargs)
        return instances[key]

    return getInstance

"""
注解获取配置文件的值 ${key1.key2}
"""
def value(value, default_value = None):
    def proxy(fn):
        def getValue(*args, **kwargs):
            result = value
            if value.startswith("${"):
                result = Container.config.getProperty(value[2: -1], default_value)
            return result
        return getValue
    return proxy

"""
注解，jwt权限校验
"""
def auth():
    def proxy(fn):
        def authHandler(*args, **kwargs):
            try:
                token = request.headers.get(RequestHeader.AUTH.value)
                if token:
                    jwt.decode(
                        token,
                        Container.config.getProperty("jwt.secret-key", "123456"),
                        options=JWT_OPTIONS
                    )
                else:
                    raise BusinessException(ResponseCode.AUTH_ERROR, None)
            except Exception as e:
                logger.error(e)
                raise BusinessException(ResponseCode.AUTH_ERROR, e)
            return fn(*args, **kwargs)
        return authHandler
    return proxy

"""
注解，获取请求的body参数，传入函数里面
param_infos：{'paramName': {'verifies': [verifyFunctionName1, verifyFunctionName2...]}}
"""
def jsons(param_infos):
    def proxy(fn):
        def jsonHandler(*args, **kwargs):
            params = request.get_json(silent=True)
            if param_infos:
                for key, param_info in param_infos.items():
                    if params:
                        value = params[key]
                        for item in param_info['verifies']:
                            item(value, ResponseCode.PARAM_ERROR)
            if params:
                kwargs = {**kwargs, **params}
            return fn(*args, **kwargs)
        return jsonHandler
    return proxy

"""
注解，获取请求的get url参数，传入函数里面
param_infos：{'paramName': {'verifies': [verifyFunctionName1, verifyFunctionName2...]}}
"""
def args(param_infos):
    def proxy(fn):
        def argsHandler(*args, **kwargs):
            thread_local.id = threading.currentThread().ident
            params = {}
            if request.args:
                for item in request.args:
                    params[item] = request.args.get(item)
            if param_infos:
                for key, param_info in param_infos.items():
                    if params:
                        value = params[key]
                        for item in param_info['verifies']:
                            item(value, ResponseCode.PARAM_ERROR)
                    else:
                        raise BusinessException(ResponseCode.PARAM_ERROR, None)
            if params:
                kwargs = {**kwargs, **params}
            return fn(*args, **kwargs)
        return argsHandler
    return proxy

"""
注解，获取请求的form参数，传入函数里面
param_infos：{'paramName': {'verifies': [verifyFunctionName1, verifyFunctionName2...]}}
"""
def form(param_infos):
    def proxy(fn):
        def formHandler(*args, **kwargs):
            params = {}
            if request.form:
                for item in request.form:
                    params[item] = request.form.get(item)
            if param_infos:
                for key, param_info in param_infos.items():
                    if params:
                        value = params[key]
                        for item in param_info['verifies']:
                            item(value, ResponseCode.PARAM_ERROR)
                    else:
                        raise BusinessException(ResponseCode.PARAM_ERROR, None)
            if params:
                kwargs = {**kwargs, **params}
            return fn(*args, **kwargs)
        return formHandler
    return proxy


'''
添加事务注解
path：需要添加事务的文件路径，如core.dao.analysis_result
'''
def transactional(path):
    def proxy(fn):
        def trans(*args, **kwargs):
            database_conn_pool = Container.database_conn_pool_dict[path]
            conn = None
            try:
                conn = database_conn_pool.getconn()
                thread_local.database_conn = conn
                result = fn(*args, **kwargs)
                conn.commit()
                return result
            except Exception as e:
                logger.error(e)
                if conn:
                    conn.rollback()
                raise e
            finally:
                if conn:
                    thread_local.database_conn = None
                    database_conn_pool.putconn(conn)
        return trans
    return proxy

'''
执行查询sql
sql：需要执行的sql
sql_inject：是否需要防止sql注入，默认需要
'''
def select(sql = "", sql_inject = True):
    def proxy(fn):
        def execute(*args, **kwargs):
            try:
                eSql = sql
                params = ()
                if len(args) > 1:
                    if type(args[1]).__name__ == "list":
                        if sql_inject:
                            params = tuple(args[1])
                        else:
                            eSql = eSql % tuple(args[1])
                    else:
                        if sql_inject:
                            params = tuple(args[1:])
                        else:
                            eSql = eSql % args[1:]
                elif kwargs and len(kwargs) > 0:
                    eSql = matchReplace(PATTERN_NAME, eSql, kwargs)
                    eSql, params = matchParams(PATTERN_PARAMS, eSql, kwargs)
                conn = None
                try:
                    conn = thread_local.database_conn
                except AttributeError as e:
                    logger.debug(e)
                if conn:
                    with conn.cursor() as curs:
                        curs.execute(eSql, params)
                        result = curs.fetchall()
                    return result
                else:
                    try:
                        path = fn.__module__[:fn.__module__.rindex(".")]
                        database_conn_pool = Container.database_conn_pool_dict[path]

                        conn = database_conn_pool.getconn()
                        with conn:
                            with conn.cursor() as curs:
                                curs.execute(eSql, params)
                                result = curs.fetchall()
                        return result
                    finally:
                        if conn:
                            database_conn_pool.putconn(conn)
            except Exception as e:
                logger.error("sql error: %s" % e)
                raise e
        return execute
    return proxy

'''
执行查询sql
sql：需要执行的sql
need_key: 是否需要返回主键，默认不需要，返回执行行数
key：主键数据库字断名
sql_inject：是否需要防止sql注入，默认需要
'''
def executeSql(sql = "", need_key = False, key = "", sql_inject = True):
    def proxy(fn):
        def execute(*args, **kwargs):
            try:
                eSql = sql
                params = ()
                if len(args) > 1:
                    if type(args[1]).__name__ == "list":
                        if sql_inject:
                            params = tuple(args[1])
                        else:
                            eSql = eSql % tuple(args[1])
                    else:
                        if sql_inject:
                            params = tuple(args[1:])
                        else:
                            eSql = eSql % args[1:]
                elif kwargs and len(kwargs) > 0:
                    eSql = matchReplace(PATTERN_NAME, eSql, kwargs)
                    eSql, params = matchParams(PATTERN_PARAMS, eSql, kwargs)
                conn = None
                try:
                    conn = thread_local.database_conn
                except AttributeError as e:
                    logger.debug(e)
                if conn:
                    with conn.cursor() as curs:
                        if need_key:
                            eSql = eSql + "RETURNING " + key
                            curs.execute(eSql, params)
                            result = curs.fetchall()
                        else:
                            curs.execute(eSql, params)
                            result = curs.rowcount
                    return result
                else:
                    try:
                        path = fn.__module__[:fn.__module__.rindex(".")]
                        database_conn_pool = Container.database_conn_pool_dict[path]
                        conn = database_conn_pool.getconn()
                        with conn:
                            with conn.cursor() as curs:
                                if need_key:
                                    eSql = eSql + "RETURNING " + key
                                    curs.execute(eSql, params)
                                    result = curs.fetchall()
                                else:
                                    curs.execute(eSql, params)
                                    result = curs.rowcount
                        return result
                    finally:
                        if conn:
                            database_conn_pool.putconn(conn)
            except Exception as e:
                logger.error("sql error: %s" % e)
                raise e
        return execute
    return proxy