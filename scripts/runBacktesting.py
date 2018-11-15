"""
Run a backtesting, in this template we run KingKeltener Strategy.
"""

from trader.app.cta.ctaBacktesting import backtestingEngine

if __name__ == "__main__":
    from trader.app.cta.strategies import KingKeltener

    engine = backtestingEngine()
    engine.setBacktestingMode(engine.BAR_MODE)

    engine.setStartDate('20120101')
    engine.setInitDate('20101212')

    engine.setDatabase(db='Jax_1Min_Db',collection='IF0000')

    engine.initStrategy(KingKeltener)

    engine.runBacktesting()

    engine.showBacktestingResult()