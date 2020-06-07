from common.run.container import logger
from web.service.history_data_analysis_service import stableUpLowAnalysis


def analysisStableUpLowJob():
    logger.info("stable up low analysis start")
    stableUpLowAnalysis()
    logger.info("stable up low analysis end")