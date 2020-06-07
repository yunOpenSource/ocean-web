import logging
import os

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from gevent import monkey
from gevent.pywsgi import WSGIServer

from common.run.container import Container, logger, app
from common.config.config_load import Config
from psycopg2.pool import ThreadedConnectionPool

class RunApplication(object):
    def __init__(self, args):
        for arg in args:
            temp = arg.split("=")
            if temp[0] == "env":
                Container.env = temp[1]
        # 获取项目根目录
        Container.project_path = os.getcwd()

        # 加载配置文件信息
        Container.config = Config(root_path=Container.project_path, env=Container.env)

        # 初始化日志
        level_info = {
            'debug': logging.DEBUG,
            'info': logging.INFO,
            'warning': logging.WARNING,
            'error': logging.ERROR
        }
        logging.basicConfig(level=level_info[Container.config.getProperty("logging.level")]
                            , format=Container.config.getProperty("logging.format"))

        logger.info("run env: %s" % Container.env)
        logger.debug("config: %s" % Container.config.config)
        logger.debug("project_root_path = %s" % Container.project_path)

        # 打印logo
        logger.info('''


                                           ('-.   ('-.         .-') _  
                                        _(  OO) ( OO ).-.    ( OO ) ) 
                .-'),-----.    .-----. (,------./ . --. /,--./ ,--,'  
               ( OO'  .-.  '  '  .--./  |  .---'| \-.  \ |   \ |  |\  
               /   |  | |  |  |  |('-.  |  |  .-'-'  |  ||    \|  | ) 
               \_) |  |\|  | /_) |OO  )(|  '--.\| |_.'  ||  .     |/  
                 \ |  | |  | ||  |`-'|  |  .--' |  .-.  ||  |\    |   
                  `'  '-'  '(_'  '--'\  |  `---.|  | |  ||  | \   |   
                    `-----'    `-----'  `------'`--' `--'`--'  `--'   
                
               ''')

        # 加载数据库
        database_list = Container.config.getProperty("postgres")
        logger.info("load database start")
        for key, database in database_list.items():
            logger.info(
                "load database, host: %s, port: %s, path: %s" % (database["host"], database["port"], database["path"]))
            Container.database_conn_pool_dict[database["path"]] \
                = ThreadedConnectionPool(database["minconn"]
                                         , database["maxconn"]
                                         , host=database["host"]
                                         , user=database["user"]
                                         , password=database["password"]
                                         , dbname=database["database"]
                                         , port=int(database["port"]))
        logger.info("load database complete")

        # 初始化定时任务
        logger.info("init scheduler start")
        Container.scheduler = BackgroundScheduler(job_defaults={
            'coalesce': Container.config.getProperty("scheduler.coalesce", False),
            'max_instances': Container.config.getProperty("scheduler.max_instances", 1),
            'misfire_grace_time': Container.config.getProperty("scheduler.misfire_grace_time", 60)
        })

        # 初始化jobs
        job_list = Container.config.getProperty("scheduler.job")
        module_dict = {}
        for key, job in job_list.items():
            logger.debug("add scheduler: %s" % key)
            func_info = job["path"].split(".")
            method = func_info[-1]
            from_info = ".".join(func_info[0: -2]) if len(func_info) > 3 else func_info[0]
            module_info = ".".join(func_info[0: -1])
            module = None
            try:
                module = module_dict[module_info]
            except Exception as e:
                logger.warn(e)
            if not module:
                module = __import__(module_info, fromlist=[from_info])
                module_dict[module_info] = module
            fn = getattr(module, method)
            if job["schema"] == "cron":
                Container.scheduler.add_job(fn, CronTrigger.from_crontab(job["cron"]))
            else:
                Container.scheduler.add_job(fn, job["schema"], seconds=job["seconds"])
        Container.scheduler.start()
        logger.info("init scheduler end")

        # 初始化web
        port = Container.config.getProperty("server.port", 8080)
        logger.info("init web start, port: %s" % port)
        routeLen = len("@route(")
        errorhandlerLen = len("@errorhandler(")
        for root, dirs, files in os.walk(Container.project_path):
            for file in files:
                with open(os.path.join(root, file), mode='r') as rp:
                    try:
                        lines = rp.readlines()
                        flag = False
                        for line in lines:
                            content = line.rstrip()
                            if len(content) > routeLen and (content[:routeLen] == "@route(" or content[:errorhandlerLen] == "@errorhandler("):
                                flag = True
                                break
                        if flag:
                            f = root[len(Container.project_path) + 1:]
                            f = ".".join(f.split("/"))
                            name = ".".join([f, file.split(".")[0]])
                            logger.info("init web, path: %s" % name)
                            __import__(name, fromlist=[f])
                    except Exception as e:
                        logger.debug("init controller failed, path: %s Exception: %s" % (os.path.join(root, file), e))
        # app.run(host="0.0.0.0", port=int(port))
        monkey.patch_all()
        http_server = WSGIServer(("0.0.0.0", port), app)
        http_server.serve_forever()
