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
        self.volume = None
        self.volumeTraded = None
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
