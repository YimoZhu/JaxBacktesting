
class ctaTemplate(object):
    className = "ctaStrategyTemplate"
    author = "Yimo Zhu"
    STATUS_SLEEPING = "Strategy sleeping"
    STATUS_INITING = "Strategy initing"
    STATUS_TRADING = "Strategy trading"
    ###############################################################
    def __init__(self,engine,settings_bounded={},settings_extended={}):
        self.engine = engine
        self.symbol = None
        self.exchange = None
        self.name = None
        
        self.frequency = None
        
        update = {}
        for field in self.__dict__:
            try:
                update[field] = settings_bounded[field]
            except:
                pass
        self.__dict__.update(update)
        self.__dict__.update(settings_extended)
    
    def onBar(self,bar):
        #Handling a bar.
        pass
    def onInitBar(self,initBar):
        #Handling a bar when initing.
        pass
    def onTick(self,tick):
        #Handling a tick.
        pass
    def onTrade(self,trade):
        pass
    def onStopOrder(self,so):
        pass