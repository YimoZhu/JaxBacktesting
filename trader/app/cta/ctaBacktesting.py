"""Backtesting Objects"""

import numpy as np
import pymongo
from trader.JaxTools import output
from datetime import datetime
from collections import OrderedDict
from trader.JaxConstant import *
from trader.JaxObjects import info_tracker,limitOrder,stopOrder,trade

class backtestingEngine(object):
    BAR_MODE = "Bar Mode"
    TICK_MODE = "Tick Mode"
    CLASS_NAME = "backtestingEngine"
    #################################################
    def __init__(self,settings_bounded={},settings_extended={}):
        #Basic Configurations
        self.mode = None                #Tick or Bar MODE
        self.symbol = None              #Trading target
        self.exchange = None            #Exchange name
        self.dbName = None                  #Target Database
        self.collectionName = None          #Target Collection

        #Infrastructures
        self.dbClient = None
        self.db = None
        self.collection = None
        self.dbCursor_init = None
        self.dbCursor_backtest = None
        self.tracker = info_tracker()
        self.__frequency = None

        #Trader
        self.backtestingStartDate = None
        self.backtestingEndDate = None
        self.initStartDate = None
        self.initEndDate = None
        self.strategyName = None
        self.strategy = None

        #Trading
        self.trading = False
        self.bar = None
        self.tick = None
        self.datetime = None
        self.date = None
        self.time = None
        self.position_long = 0
        self.position_short = 0
        self.limitOrderCount = 0
        self.stopOrderCount = 0
        self.tradeCount = 0
        self.workingStopOrdersDict = OrderedDict()
        self.workingLimitOrdersDict = OrderedDict()
        #Others
        self.mustHave=["mode",'backtesting']

        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)

        self.tracker.frequency = self.__frequency

    @property
    def frequency(self):
        return self.__frequency
    @frequency.setter
    def frequency(self,value):
        self.__frequency = value
        self.tracker.frequency = value

    @property
    def position_net(self):
        return self.position_long - self.position_short

    def check_setup(self,checkList):
        #Pass in the checkList, then check wether all parameters in the checklist has been specified.
        for var in self.mustHave:
            missingList = []
            if var not in self.__dict__:
                missingList.append(var)
        if len(missingList) != 0:
            print("Not Completely Setup, missing parameters %s"%(missingList))
            raise ValueError
        else:
            print("All necessary parameter have been specified!")
    
    def setup_db(self):
        #Connect to Mongodb
        print("Connecting db...")
        self.dbClient = pymongo.MongoClient("Localhost",27017)
        print('Connected to Mongodb, Host: Localhost, Port: 27017')
        
        #Set dbcursors
        self.db = self.dbClient[self.dbName]
        self.collection = self.db[self.collectionName]
        self.dbCursor_init = self.collection.find_many({"Date":{"$gte":int(self.initStartDate),"$lte":int(self.initEndDate)}})
        self.dbCursor_backtest = self.collection.find_many({"Date":{"$gte":int(self.backtestingStartDate),"$lte":int(self.backtestingEndDate)}})
        print("successfully setup db cursors.")

    def runBacktesting(self):
        #First check the parameters' completion.
        self.check_setup(self.mustHave)
        self.setup_db()
        if self.mode == self.BAR_MODE:
            func = self.newBar
        elif self.mode == self.TICK_MODE:
            func = self.newTick

        #Run backtesting
        print("Start Backtesting.....")
        self.trading = True

        print("Initing Strategy...")
        for initBar in self.dbCursor_init:
            self.strategy.onInitBar(initBar)
        print("Strategy Inited!")

        output("Start replaying data...")
        for bar in self.dbCursor_backtest:
            func(bar)
        output("Finished replaying data.")
        self.trading = False

    def newBar(self,bar):
        #The logic of handling a new bar.
        #Updating the date and time.
        self.bar = bar
        self.date = bar.Date
        self.time = bar.time
        year = self.date%10000
        month = self.date%100- year*100
        day = self.date - year*10000 - month*100
        hour,minute,second = [int(x) for x in self.time.split(':')]
        self.datetime = datetime(year,month,day,hour,minute,second)
        #Tracking the pop up of the new bar.
        self.tracker.newBar(bar)
        #Triggering the local stop orders.
        self.triggerStopOrders()
        #Cross the newly updated limit orders.
        self.crossLimitOrders()

    def newTick(self,tick):
        #The logic of handling a new tick.
        pass

    def triggerStopOrders(self):
        """The logic to corss previously buried local stop oders"""
        for soID,so in self.workingLimitOrdersDict.items():
            if so.direction == DIRECTION_LONG:
                triggered = (self.bar.High>=so.price)
            elif so.direction == DIRECTION_SHORT:
                triggered = (self.bar.Low<=so.price)
            else:
                triggered = False
            if triggered:
                #If the stop order is triggered
                so.status = SOSTATUS_TRIGGERED
                so.datetimeTriggered = self.datetime
                #Track the new info
                self.tracker.stopOrderTriggered(so)
                #Judge the new order
                if so.offset == OFFSET_CLOSE:
                    #If the offset is close, then we have to make sure wether there's still nececssity to close the postition
                    if (self.postition_long>0 & so.direction == DIRECTION_SHORT):
                        #There is long position in hand
                        self.sendOrder(so.price,so.volume,orderType=so.orderType)
                    elif (self.position_short>0 & so.direction == DIRECTION_LONG):
                        #There is shor position in hand
                        self.sendOrder(so.price,so.volume,orderType=so.orderType)
                elif so.offset == OFFSET_OPEN:
                    #If the offset is open, then we can just send the new order out withou check the current position.
                    self.sendOrder(so.price,so.volume,so.orderType)
                #Delete the triggered stop order from working dictionary
                del self.workingStopOrdersDict[so.soID]
    
    def crossLimitOrders(self):
        #Cross the working limit orders according to the newly updated infos.
        buyCrossPrice = self.bar.Low
        sellCrossPrice = self.bar.High
        for orderID,order in self.workingLimitOrdersDict.items():
            buyCrossed = (order.direction == DIRECTION_LONG & order.price >= buyCrossPrice)
            sellCrossed = (order.direction == DIRECTION_SHORT & order.price <= sellCrossPrice)

            if buyCrossed:
                price = min(self.bar.Open,order.price)
                #First update the info of the order.
                order.priceTraded = price
                order.status = STATUS_ALLTRADED
                order.datetimeLastTraded = self.datetime
                order.volumeTraded = order.volume
                #Update position
                if order.offset == OFFSET_OPEN:
                    self.position_long = self.position_long + order.volume
                elif order.offset == OFFSET_CLOSE:
                    self.position_short = self.position_short - order.volume
                #Then shaping a new trade object.
                self.tradeCount += 1
                newTrade = trade(settings_bounded=order.__dict__,
                                 settings_extended={'tradeID':self.tradeCount,'datetimeCreated':self.datetime,'price':price})
            elif sellCrossed:
                price = max(self.bar.Open,order.price)
                order.priceTraded = price
                order.status = STATUS_ALLTRADED
                order.datetimeLastTraded = self.datetime
                order.volumeTraded = order.volume
                #Update position
                if order.offset == OFFSET_OPEN:
                    self.position_short = self.position_short + order.volume
                elif order.offset == OFFSET_CLOSE:
                    self.position_long = self.position_long - order.volume
                #Shaping a new trade object
                self.tradeCount += 1
                newTrade = trade(settings_bounded=order.__dict__,
                                 settings_extended={'tradeID':self.tradeCount,'datetimeCreated':self.datetime,'price':price})
           
            if buyCrossed|sellCrossed:
                #Keep track of this new trade.
                self.tracker.newTrade(newTrade)
                #Delete the working limit order
                del self.workingLimitOrdersDict[orderID]
            else:
                pass
    def sendOrder(self,price,volume,orderType,stop=False,feedback=False):
        #logic of sending order
        try:
            if stop == False:
                self.limitOrderCount += 1
                #send limitOrder
                #Shaping the limit order parameters
                order = limitOrder()
                order.symbol = self.symbol
                order.exchange = self.exchange
                order.strategy = self.strategy
                order.datetimeCreated = self.datetime
                order.price = price
                order.orderID = self.limitOrderCount
                if orderType == ORDERTYPE_BUY:
                    order.direction = DIRECTION_LONG
                    order.offset = OFFSET_OPEN
                    order.orderType = ORDERTYPE_BUY
                elif orderType == ORDERTYPE_SELL:
                    order.direction = DIRECTION_SHORT
                    order.offset = OFFSET_CLOSE
                    order.orderType = ORDERTYPE_SELL
                elif orderType == ORDERTYPE_SHORT:
                    order.direction = DIRECTION_SHORT
                    order.offset = OFFSET_OPEN
                    order.orderType = ORDERTYPE_SHORT
                elif orderType == ORDERTYPE_COVER:
                    order.direction = DIRECTION_LONG
                    order.offset = OFFSET_CLOSE
                    order.orderType = ORDERTYPE_COVER
                #We should consider bound the close order's volume.
                if order.offset == ORDERTYPE_SELL:
                    order.volume = min(self.position_long,volume)
                elif order.offset == ORDERTYPE_COVER:
                    order.volume = min(self.position_short,volume)
                else:
                    order.volume = volume
                #Add to workinglimitorder dictionary
                self.workingLimitOrdersDict[order.orderID] = order
                #Add tracking infos
                self.tracker.newLimitOrder(order)
                if feedback == True:
                    return FEEDBACK_LIMITORDERSENT
                else:
                    pass
            elif stop == True:
                self.stopOrderCount += 1
                #send stopOrder
                #First shape a stop order
                settings = {'soID':self.stopOrderCount,'symbol':self.symbol,'exchange':self.exchange,'strategy':self.strategy,
                            'datetimeCreated':self.datetime,'price':price,'volume':volume}
                so = stopOrder(settings_bounded=settings)
                if orderType == ORDERTYPE_BUY:
                    so.direction = DIRECTION_LONG
                    so.offset = OFFSET_OPEN
                elif orderType == ORDERTYPE_COVER:
                    so.direction = DIRECTION_LONG
                    so.offset = OFFSET_CLOSE
                elif orderType ==ORDERTYPE_SELL:
                    so.direction = DIRECTION_SHORT
                    so.offset = OFFSET_CLOSE
                elif orderType ==ORDERTYPE_SHORT:
                    so.direction = DIRECTION_SHORT
                    so.offset = OFFSET_OPEN
                so.orderType = orderType
                #then send the order to local dictionary
                self.workingStopOrdersDict[so.soID] = so
                #Add tracking infos
                self.tracker.newStopOrder(so)
                if feedback == True:
                    return FEEDBACK_STOPORDERBURIED
                else:
                    pass
        except:
            self.tracker.orderFailure(self.datetime)
            if feedback == True:
                return FEEDBACK_ORDERFAILURE
            else:
                pass

