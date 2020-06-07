from common.annotation.decorators import value


class TestService(object):
    @value("${logging.level}")
    def getLevel(self):
        pass