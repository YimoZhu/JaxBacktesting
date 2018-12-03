from trader.app.cta.ctaBacktesting import backtestingEngine
from trader.JaxConstant import *
from trader.app.cta.strategies import Kingkeltener

engine = backtestingEngine({"dbName":"Jax_1Min_Db","collectionName":"IF0000","symbol":"IF0000",
                            "initStartDate":"20100101","initEndDate":"20100417","backtestingStartDate":"20100418",
                            "backtestingEndDate":"20110101"})
engine.mode = engine.BAR_MODE
engine.strategy = Kingkeltener.strategyKingKeltener(engine)

engine.runBacktesting()
