#Strategy file KingKeltener
import numpy as numpy
from trader.app.cta.ctaTemplate import ctaTemplate
from trader.JaxObjects import BarGenerator
from trader.JaxConstant import *
import talib 

class strategyKingKeltener(ctaTemplate):
    className = "ctaStrategyKingKeltener"
    author = "Yimo Zhu"
    logic = "We use 5 minute bar, and whenever the k-line hit one of the trail we set the break through order"
    def __init__(self,settings_bounded={},settings_extended={}):
        super().__init__(settings_bounded,settings_extended)
        
        #Parameters
        self.frequency = FREQUENCY_INTERDAY
        self.kkDev = 1.5
        self.kkLength = 11
        self.initDays = 10
        self.tradeSize = 1
        self.trailingPrcnt = 1.5

        #Variables
        self.kkUp = None
        self.kkDown = None
        self.center = None
    
        self.bg = BarGenerator()

    def onInitBar(self,ib):
        #How to handel a bar when initing.
        self.