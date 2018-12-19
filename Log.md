#Develop Log
2018.11.13   
Start Moving Previous Work to this directory, migrate from 2.7 to 3.7 version and use a multiprocessing backtesting instead of data replay.

2018.12.15
The trading result calculation is broken down into several parts:
1. The daily result object.
2. Every bar prompted, we update the close price in the "daily result" object.
3. When the result is called to be shown, we start to calculate it.
4. The calculation process is check the trades one by one and generate "trading result" object. It's exactly the unit for KPI calculation, with entry and exit prices and dates.
5. After calculating the "trading result", we start to aggregate them one by one and generate all KPI.