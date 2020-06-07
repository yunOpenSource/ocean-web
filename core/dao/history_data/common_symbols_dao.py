from common.annotation.decorators import singleton, select


@singleton
class CommonSymbolsDao(object):
    """
    查询symbols
    """
    @select("select symbol from eagle.common_symbols")
    def selectSymbols(self): pass
