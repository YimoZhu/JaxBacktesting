class info_logger(object):
    """
    Keep tracking all the trading infos for an engine.
    """
    def __init__(self,settings={}):

        self.__dict__.update(settings)