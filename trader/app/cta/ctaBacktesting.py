"""Backtesting Objects"""

import numpy as np
import pymongo
from trader.JaxTools import output
from datetime import datetime
from collections import OrderedDict
from trader.JaxConstant import *
from trader.JaxObjects import info_tracker,limitOrder,stopOrder

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
        self.limitOrderCount = 0
        self.stopOrderCount = 0
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

    def triggerStopOrders(self):
        """The logic to corss previously buried local stop oders"""


    def sendOrders(self,price,volume,orderType,stop=False,feedback=False):
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
                order.volume = volume
                order.volume = 0
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
            info_tracker.orderFailure(self.datetime)
            if feedback == True:
                return FEEDBACK_ORDERFAILURE
            else:
                pass













































