from collections import OrderedDict
from trader.JaxTools import appendTime

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
        if self.frequency =
        self.logger.append(appendTime("Sending a new limit order, order ID %s, price: %s, volume: %s"%order.orderID))



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
        self.status = None

        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)