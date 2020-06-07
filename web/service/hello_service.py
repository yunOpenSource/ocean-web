from common.annotation.decorators import transactional
from common.run.container import logger
from core.dao.analysis_result.symbol_analysis_stable_rise_dao import SymbolAnalysisStableRiseDao


@transactional("core.dao.analysis_result")
def hello():
    id = SymbolAnalysisStableRiseDao().insertPerson(["aa", 10])
    logger.info(id)
    id = SymbolAnalysisStableRiseDao().insertPerson(["aaf", 11])
    logger.info(id)

