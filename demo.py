from trader.app.cta.ctaBacktesting import backtestingEngine
from trader.JaxConstant import *
engine = backtestingEngine({'__frequency':FREQUENCY_INNERDAY})

engine.frequency = FREQUENCY_INNERDAY

print(engine.frequency)
print(engine.tracker.frequency)