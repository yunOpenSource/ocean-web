from common.annotation.decorators import singleton, select


@singleton
class MarketKLineMinDao(object):

    """
    根据symbol查询k线数据
    """
    @select("select * from eagle.market_kline_min_%s order by timestamp asc")
    def selectMarketKlineMins(self, symbol): pass

