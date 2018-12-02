#Strategy file KingKeltener
import numpy as np
from trader.app.cta.ctaTemplate import ctaTemplate
from trader.JaxObjects import BarGenerator,ArrayManager
from trader.JaxConstant import *

class strategyKingKeltener(ctaTemplate):
    className = "ctaStrategyKingKeltener"
    author = "Yimo Zhu"
    logic = "We use 5 minute bar, and whenever the k-line hit one of the trail we set the break through order"
    def __init__(self,engine,settings_bounded={},settings_extended={}):
        super().__init__(engine,settings_bounded,settings_extended)
        
        #Parameters
        self.frequency = FREQUENCY_INNERDAY
        self.kkDev = 1.5
        self.kkLength = 11
        self.initDays = 10
        self.tradeSize = 1
        self.trailingPrcnt = 1.5            #Stop loss percent

        #Variables
        self.kkUp = None
        self.kkDown = None
        self.kkCenter = None
        self.intraTradeHigh = -np.inf               #The highest price in a 
        self.intraTradeLow = np.inf         

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
        self.engine.cancelAll()

        #First we update the variables. When it's promped
        self.ar.updateBar(xBar)
        if self.ar.isFilled == False:
            return None
        self.kkDown,self.kkCenter,self.kkUp = self.ar.kingKeltner(self.kkLength,self.kkDev)
        
        #If current position is zero, then send OCO
        if self.engine.position_net == 0:
            self.intraTradeHigh = xBar.High
            self.intraTradeLow = xBar.Low
            self.sendOCO(self.kkUp,self.kkDown,self.tradeSize)

        #If current position is positive, then track the price to quit.
        elif self.engine.position_net > 0 :
            self.intraTradeHigh = max(xBar.High,self.intraTradeHigh)
            self.intraTradeLow = min(xBar.Low,self.intraTradeLow)
            self.engine.sendOrder(self.intraTradeHigh*(1-self.trailingPrcnt/100),
                                  self.engine.position_net,ORDERTYPE_SELL,True)
        
        #If current position is negative, then track the price to quit.
        elif self.engine.position_net < 0 :
            self.intraTradeHigh = max(xBar.High,self.intraTradeHigh)
            self.intraTradeLow = min(xBar.Low,self.intraTradeLow)
            self.engine.sendOrder(self.intraTradeLow*(1+self.trailingPrcnt/100),
                                  self.engine.position_net,ORDERTYPE_COVER,True)

    def sendOCO(self,high,low,volume):
        #Send "One Cancel Other" Orders.
        self.engine.sendOrder(high,volume,ORDERTYPE_BUY,True)
        self.engine.sendOrder(low,volume,ORDERTYPE_SHORT,True)
