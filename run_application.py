from common.run.run_application import RunApplication
import sys




class DataAnalysisApplication(RunApplication):
    def __init__(self, args):
        RunApplication.__init__(self, args)

if __name__ == "__main__":
    DataAnalysisApplication(sys.argv)
