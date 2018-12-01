#Strategy file KingKeltener
import numpy as numpy
from trader.app.cta.ctaTemplate import ctaTemplate
from trader.JaxObjects import BarGenerator,ArrayManager
from trader.JaxConstant import *

class strategyKingKeltener(ctaTemplate):
    className = "ctaStrategyKingKeltener"
    author = "Yimo Zhu"
    logic = "We use 5 minute bar, and whenever the k-line hit one of the trail we set the break through order"
    def __init__(self,settings_bounded={},settings_extended={}):
        super().__init__(settings_bounded,settings_extended)
        
        #Parameters
        self.frequency = FREQUENCY_INNERDAY
        self.kkDev = 1.5
        self.kkLength = 11
        self.initDays = 10
        self.tradeSize = 1
        self.trailingPrcnt = 1.5

        #Variables
        self.kkUp = None
        self.kkDown = None
        self.kkCenter = None
        
        #Infrastructure     
        self.bg = BarGenerator(5,self.on5MinBar,self)
        self.ar = ArrayManager(self.kkLength)

        #Flags
        self.status = self.STATUS_SLEEPING

    def onInitBar(self,initBar):
        #How to handel a bar when initing.
        #In this strategy, what we need to do is to calculate the variables.
        self.status = self.STATUS_INITING
        self.bg.onBar(initBar)

    def onBar(self,bar):
        #How to handel a new minute bar when trading.
        self.status = self.STATUS_TRADING
        self.bg.onBar(bar)

    def on5MinBar(self,xBar):
        #How to handel the aggregated 5 minutes bar prompted by the bar generator.
        #First we update the variables.
        self.ar.updateBar(xBar)
        self.