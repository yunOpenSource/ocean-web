import logging
from flask import Flask

logger = logging.getLogger(__name__)
app = Flask(__name__)
route = app.route
errorhandler = app.errorhandler
class Container(object):
    project_path = ""
    env = "default"
    config = None
    database_conn_pool_dict = {}
    scheduler = None