from common.annotation.decorators import singleton, executeSql


@singleton
class SymbolAnalysisStableRiseDao(object):

    @executeSql(
        "insert into eagle.symbol_analysis_stable_rise(symbol, all_count, meet_count, stable_durations, max_rises, min_rises, middle_lowest_rises, max_yield, stop_loss) values('%s', %s, %s, '%s', '%s', '%s', '%s', %s, %s)")
    def insert(self, stable_rise_info): pass

    @executeSql("truncate table eagle.symbol_analysis_stable_rise")
    def truncate(self): pass

    @executeSql(sql="insert into public.person(name, age) values(%s, %s)", need_key=True, key="id")
    def insertPerson(self, person): pass
