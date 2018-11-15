"""Backtesting Objects"""

import numpy as np

class backtestingEngine(object):
    BAR_MODE = "Bar Mode"
    TICK_MODE = "Tick Mode"
    CLASS_NAME = "backtestingEngine"

    #################################################
    def __init__(self,settings={}):
        #Basic Configurations
        self.mode = None
        
        #Infrastructures
        self.dbCursor = None

        #Trader
        self.backtestingDate = None
        self.initDate = None

        #Trading
        self.
        #Others
        self.mustHave=["mode",'backtesting']

        self.__dict__.update(settings)
        
    def check_setup(self,checkList=self.mustHave):
        #Pass in the checkList, then check wether all parameters in the checklist has been specified.
        for var in self.mustHave:
            missingList = []
            if var == None:
                missingList.append(var)
        if len(missingList) != 0:
            print("Not Completely Setup, missing parameters %s"%(missingList))
            raise ValueError
        else:
            print("All necessary parameter have been specified!")
    
    def runBacktesting(self):
        #First check the parameters' completion.
        self.check_setup()
        
