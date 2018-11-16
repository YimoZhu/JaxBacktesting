from time import ctime

def output(msg,mode="default"):
    if mode == "default":
        print("[%s] %s"%(ctime(),msg))

def appendTime(msg,mode='default'):
    if mode == "default":
        return "[%s] %s"%(ctime(),msg)