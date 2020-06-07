import yaml

class Config():
    def __init__(self, root_path = "", env = ""):
        self.config_path = root_path + "/common/resources/application.yml"
        if env != "default":
            self.config_path = root_path + "/common/resources/application-%s.yml" % env
        with open(self.config_path, "r") as yml_file:
            self.config = yaml.load(yml_file)

    def getProperty(self, key, default_value = None):
        keys = key.split(".")
        result = self.config
        try:
            for k in keys:
                result = result[k]
        except:
            result = None
        if not result:
            result = default_value
        return result