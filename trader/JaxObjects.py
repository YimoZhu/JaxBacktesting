from collections import OrderedDict
from trader.JaxTools import appendTime
from trader.JaxConstant import *



class info_tracker(object):
    """
    Keep tracking all the trading infos for an engine.
    """
    ###########################################
    def __init__(self,settings_bounded={},settings_extended={}):
        self.frequency = None
        self.logger = []
        self.limitOrderDict = OrderedDict()
        self.stopOrderDict = OrderedDict()
        self.historyBars = []
        self.historyTicks = []
        self.historyTrade = OrderedDict()

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
            self.logger.append(appendTime("Prompting a new bar, bar datetime %s %s"%(bar.Date,bar.time)))
        else:
            self.logger.append(appendTime("Prompting a new bar, bar datetime %s"%bar.Date))

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
class trade(object):
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
    def __init__(self,freq=5):
        self.freq = freq
        self.xminBar = None
        self.bar = None

        self.callBack = lambda x:None
        self.strategy = None

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