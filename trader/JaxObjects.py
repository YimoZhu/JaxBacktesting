from collections import OrderedDict
from trader.JaxTools import appendTime
from trader.JaxConstant import *
from datetime import datetime
import numpy as np
import talib

class info_tracker(object):
    """
    Keep tracking all the trading infos for an engine.
    """
    ###########################################
    def __init__(self,settings_bounded={},settings_extended={}):
        self.frequency = None
        self.logger = []
        
        self.limitOrderDict = OrderedDict()                 #All of the limit orders that has been placed
        self.stopOrderDict = OrderedDict()                  #All of the stop orders that has been placed

        self.historyBars = []                               #All of fundamental bars
        self.historyTicks = []                              #All fundamental ticks
        self.historyTrade = OrderedDict()                   #All trades happened
        self.dailyResultDict = OrderedDict()                #Every day's result
        self.backTestingResult = {}                         #The backtestingresult dictionary calculated by function "calculateBacktestingResult"

        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)

    def newBar(self,bar):
        #Tracking the pop up of a new bar
        self.historyBars.append(bar)
        if hasattr(bar,"Time"):
            self.logger.append(appendTime("Prompting a new bar, bar datetime %s %s"%(bar.Date,bar.Time)))
        else:
            self.logger.append(appendTime("Prompting a new bar, bar datetime %s"%bar.Date))
        #Update daily result.
        self.updateDailyClose(bar.datetime,bar.Close)

    def newLimitOrder(self,order):
        #Track the info of sending a new limit order
        self.limitOrderDict[order.orderID] = order
        if self.frequency == FREQUENCY_INNERDAY:
            self.logger.append(appendTime("Sending a new limit order TYPE *%s* at time %s, order ID %s, price: %s, volume: %s"%(order.orderType,order.datetimeCreated.time(),order.orderID,order.price,order.volume))) 
        elif self.frequency == FREQUENCY_INTERDAY:
            self.logger.append(appendTime("Sending a new limit order TYPE *%s*, order ID %s, price: %s, volume: %s"%(order.orderType,order.orderID,order.price,order.volume)))
    
    def newStopOrder(self,so):
        #Track the info of sending a new stop order
        self.stopOrderDict[so.soID] = so
        if self.frequency == FREQUENCY_INNERDAY:
            self.logger.append(appendTime("Burying a new stop order TYPE *%s* at time %s, order ID %s, price: %s, volume: %s"%(so.orderType,so.datetimeCreated.time(),so.soID,so.price,so.volume))) 
        elif self.frequency == FREQUENCY_INTERDAY:
            self.logger.append(appendTime("Burying a new stop order TYPE *%s*, order ID %s, price: %s, volume: %s"%(so.offset,so.orderID,so.price,so.volume)))
    
    def orderFailure(self,dateTime):
        #Track the info of failure sending an order
        self.logger.append(appendTime("Fail to send an order at datetime %s"%dateTime))

    def stopOrderTriggered(self,so):
        #Track the info of triggering a previous stop order
        msg = "|%s| The stop order %s is triggered."%(so.datetimeTriggered,so.soID)
        self.logger.append(appendTime(msg))
    
    def newTrade(self,trade):
        #Track the info of fulfilling a new trade.
        self.historyTrade[trade.tradeID] = trade
        msg = "|%s| New trade %s, offset is %s, direction is %s, price %s, volume %s"%(trade.datetimeCreated,trade.tradeID,trade.offset,trade.direction,trade.price,trade.volume)
        self.logger.append(appendTime(msg))
    
    def writeLog(self,msg):
        #Write a log into logger
        self.logger.append(appendTime(msg))

    def updateDailyClose(self,dt,close):
        #Update the daily close price
        date = dt.date
        if date in self.dailyResultDict:
            self.dailyResultDict[date].Close = close
        else:
            self.dailyResultDict[date] = dailyResult(date,close)

##########################################################################################################
class barObject(object):
    #Characterizing a bar object.(ORM)
    def __init__(self,settings_bounded={},settings_extended={}):
        self.Open = None
        self.High = None
        self.Low = None
        self.Close = None
        self.TotalVolume = None
        self.OpenInterest = None
        self.Date = None
        self.Time = None
        
        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)

    @property
    def datetime(self):
        #Shaping the datetime
        year = int((self.Date - self.Date%10000)/10000)
        month = int((self.Date - self.Date%100)/100- year*100)
        day = int(self.Date%100)
        hour,minute,second = [int(x) for x in self.Time.split(':')]
        return datetime(year,month,day,hour,minute,second)


##########################################################################################################
class limitOrder(object):
    #Characterizing a limit order
    def __init__(self,settings_bounded={},settings_extended={}):
        self.symbol = None
        self.exchange = None
        self.strategy = None
        self.orderID = None

        self.datetimeCreated = None
        self.datetimeLastTraded = None
        self.datetimeCancelled = None

        self.price = None
        self.priceTraded = None
        self.volume = None
        self.volumeTraded = 0
        self.status = STATUS_NONTRADED
        self.direction = None
        self.offset = None
        self.orderType = None
        
        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)


########################################################################################################
class stopOrder(object):
    #characterizing a local stop order.
    def __init__(self,settings_bounded={},settings_extended={}):
        self.symbol = None
        self.exchange = None
        self.strategy = None
        self.soID = None

        self.datetimeCreated = None
        self.datetimeTriggered = None
        self.datetimeCancelled = None               

        self.price = None
        self.volume = None
        self.status = SOSTATUS_NONTRIGGERED
        self.direction = None
        self.offset = None        
        self.orderType = None
        
        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)


#########################################################################################
class tradeObject(object):
    #Characterizing a trade.
    def __init__(self,settings_bounded={},settings_extended={}):
        self.symbol = None
        self.exchange = None
        self.strategy = None
        self.tradeID = None

        self.datetimeCreated = None
        
        self.price = None
        self.volume = None
        self.direction = None
        self.offset = None

        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)


########################################################################
class BarGenerator(object):
    #Aggregating minute bar to k-minutes bar.
    def __init__(self,freq=5,callBack=lambda x:None,strategy=None):
        self.freq = freq
        self.xminBar = None
        self.bar = None

        self.callBack = callBack
        self.strategy = strategy

    def onBar(self,bar):
        if self.bar == None:
            self.bar = bar
        else:
            self.bar.High = max(self.bar.High,bar.High)
            self.bar.Low = min(self.bar.Low,bar.Low)
            self.bar.Close = bar.Close
        if bar.datetime.minute%self.freq == 0:
            self.xminBar = self.bar
            self.bar = None
            self.pushXminBar(self.xminBar)
        else:
            pass

    def pushXminBar(self,xminBar):
        #Push the x minutes bar to strategy
        self.callBack(xminBar)


#########################################################################
class ArrayManager(object):
    #Contain a certain length of bar arrays in pure data, and calculate the indicators.
    def __init__(self,length):
        #Containers
        self.openArray = np.empty(length)
        self.highArray = np.empty(length)
        self.lowArray = np.empty(length)
        self.closeArray = np.empty(length)

        #Parameters
        self.length = length
        self.leftover = length

        #Flags
        self.isFilled = False
    
    def updateBar(self,bar):
        #How to update a new bar into containers.
        if self.isFilled == False:
            self.openArray[self.length - self.leftover] = bar.Open
            self.highArray[self.length - self.leftover] = bar.High
            self.lowArray[self.length - self.leftover] = bar.Low
            self.closeArray[self.length - self.leftover] = bar.Close
            self.leftover = self.leftover - 1
            if self.leftover == 0:
                self.isFilled = True
        elif self.isFilled == True:
            self.openArray[:-1] = self.openArray[1:]
            self.highArray[:-1] = self.highArray[1:]
            self.lowArray[:-1] = self.lowArray[1:]
            self.closeArray[:-1] = self.closeArray[1:]
            self.openArray[-1] = bar.Open
            self.highArray[-1] = bar.High
            self.lowArray[-1] = bar.Low
            self.closeArray[-1] = bar.Close
    
    def sma(self,n,array=False):
        #Return the n-periods simple moving average.
        result = talib.SMA(self.closeArray,n)
        if array == True:
            return result
        else:
            return result[-1]

    def atr(self,n,array=False):
        #Return the n-periods average true range.
        result = talib.ATR(self.highArray,self.lowArray,self.closeArray,n)
        if array == True:
            return result
        else:
            return result[-1]

    def kingKeltner(self,n,kkdev,array=False):
        #King keltner tunnel.
        kkcenter = self.sma(n,array)
        atr = self.atr(n,array)
        kkup = kkcenter + kkdev*atr
        kkdown = kkcenter - kkdev*atr
        return kkdown,kkcenter,kkup


class dailyResult(object):
    #Trading result of day.
    def __init__(self,date,closePrice,settings_bounded = {},settings_extended={}):
        self.date = date
        self.closePrice = closePrice
        
        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)