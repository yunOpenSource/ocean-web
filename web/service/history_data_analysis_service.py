import decimal
import json

from common.annotation.decorators import value
from common.run.container import logger
from core.dao.analysis_result.symbol_analysis_stable_rise_dao import SymbolAnalysisStableRiseDao
from core.dao.history_data.common_symbols_dao import CommonSymbolsDao
from core.dao.history_data.market_kline_min_dao import MarketKLineMinDao
import pandas as pd
import numpy as np

from common.util.constant_util import KLINE_MIN_COLUMNS, STABLE_UP_LOW_COLUMNS

@value("${data-analysis.stable-max-rise}")
def getStableMaxRise(): pass

@value("${data-analysis.rise-after-rise}")
def getRiseAfterRise(): pass

@value("${data-analysis.rise-duration}")
def getRiseDuration(): pass

def stableUpLowAnalysis():
    symbols = CommonSymbolsDao().selectSymbols()
    logger.debug("need handler symbols: %s" % symbols)
    stable_up_low_list = []
    # symbols = [("ethusdt",)]
    for symbol_tuple in symbols:
        try:
            symbol = symbol_tuple[0]
            logger.info("symbol: %s analysis start" % symbol)
            kline_min_datas = MarketKLineMinDao().selectMarketKlineMins(symbol)
            if kline_min_datas:
                kline_min_table = pd.DataFrame(kline_min_datas, columns=KLINE_MIN_COLUMNS)
                stable_up_low_list.append([symbol] + analysisStableUpLow(np.array(kline_min_table["rise_fall_amplitude"]), getStableMaxRise(), getRiseAfterRise(), getRiseDuration()))
            logger.info("symbol: %s analysis end" % symbol)
        except Exception as e:
            logger.error("symbol: %s error: %s" % (symbol, e))
    stable_up_low_table = pd.DataFrame(stable_up_low_list, columns=STABLE_UP_LOW_COLUMNS)

    result_list = []
    for index in range(len(stable_up_low_table)):
        temp = stable_up_low_table[index:index + 1]
        # if np.array(temp["count"])[0] == 0:
        # continue
        symbol = np.array(temp["symbol"])[0]
        a = decimal.Decimal(str(np.array(temp["all_count"])[0]))

        max_x = 0
        stop_loss = 0
        middle_low_list = np.array(temp["middle_lows"])[0]
        for item in middle_low_list:
            item_de = decimal.Decimal(item)
            y = 0
            for y_item in middle_low_list:
                if item_de <= decimal.Decimal(y_item):
                    y += 1
            x = (decimal.Decimal(0.05) * decimal.Decimal(y) + (
                        decimal.Decimal(a) - decimal.Decimal(y)) * item_de) / decimal.Decimal(a)
            if max_x < x:
                max_x = x
                stop_loss = item_de
        result_list.append([symbol, a, np.array(temp["count"])[0], json.dumps(np.array(temp["stable_duration"])[0]), json.dumps(np.array(temp["max_percents"])[0]), json.dumps(np.array(temp["min_percents"])[0]), json.dumps(np.array(temp["middle_lows"])[0]), max_x, stop_loss])
    symbol_analysis_stable_rise_dao = SymbolAnalysisStableRiseDao();
    symbol_analysis_stable_rise_dao.truncate()
    for result in result_list:
        symbol_analysis_stable_rise_dao.insert(result)


def analysisStableUpLow(rise_fall_amplitude_list, stable_rate, up_rate, up_minute):
    count = 0
    all_count = 0
    index = 0
    stable_percent = 0
    lens = len(rise_fall_amplitude_list)
    stable_duration = []
    min_percents = []
    max_percents = []
    middle_lows = []
    stable_count = 0
    count_2 = 0
    count_3 = 0
    count_5 = 0
    count_8 = 0
    while index < lens:
        stable_count += 1
        stable_percent += rise_fall_amplitude_list[index]
        if stable_percent >= stable_rate:
            min_percent = 0
            max_percent = 0
            all_count += 1
            up_percent = 0
            up_index = index + 1
            end_index = up_index + up_minute
            middle_low = 0
            while up_index < lens and up_index < end_index:
                up_percent += rise_fall_amplitude_list[up_index]
                up_index += 1
                if up_percent > max_percent:
                    max_percent = up_percent
                if up_percent < min_percent:
                    min_percent = up_percent
                if up_percent >= up_rate:
                    middle_low = min_percent
            if max_percent >= up_rate:
                count += 1
                middle_lows.append("%s" % middle_low)
                if middle_low >= -0.02:
                    count_2 += 1
                if middle_low >= -0.03:
                    count_3 += 1
                if middle_low >= -0.05:
                    count_5 += 1
                if middle_low >= -0.08:
                    count_8 += 1
            index = end_index
            stable_percent = 0
            stable_duration.append(stable_count)
            max_percents.append("%s" % max_percent)
            min_percents.append("%s" % min_percent)
            stable_count = 0
        elif stable_percent <= -stable_rate:
            index += 1
            stable_percent = 0
        else:
            index += 1
    logger.info("横盘%s后%s分钟内上涨%s个数: %s, 总数: %s, 横盘: %s, 最大: %s, 最小: %s, 中间最小值: %s" % (
    stable_rate, up_minute, up_rate, count, all_count, stable_duration, max_percents, min_percents, middle_lows))
    return [all_count, count, stable_duration, max_percents, min_percents, middle_lows, count_2, count_3, count_5,
            count_8]
