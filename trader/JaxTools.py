from time import ctime

def output(msg,mode="defalt"):
    if mode == "default":
        print("[%s] %s"%(ctime(),msg))