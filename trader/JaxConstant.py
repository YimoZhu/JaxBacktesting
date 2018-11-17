#Event Types
EVENT_SENDLIMITORDER = 'SendLimitOrder'
EVENT_BURYSTOPORDER = 'BuryStopOrder'

#Trading Frequencies
FREQUENCY_INNERDAY = "Inner day"
FREQUENCY_INTERDAY = "Inter day"

#Limit Order Status
STATUS_NONTRADED = 'Nontraded'
STATUS_PARTIALTRADED = 'Partial traded'
STATUS_ALLTRADED = 'All traded'
STATUS_CANCELLED = "cancelled"

#Local Stop Order Status
SOSTATUS_NONTRIGGERED = "So Nontriggered"
SOSTATUS_TRIGGERED = "So triggered"
SOSTATUS_CANCELLED = "So cancelled"

#Offset, Direction and Order types
OFFSET_OPEN = "Offset Open"
OFFSET_CLOSE = 'Offset Close'

DIRECTION_LONG = "Direction Long"
DIRECTION_SHORT = "Direction Short"

ORDERTYPE_BUY = "Buy"
ORDERTYPE_SELL = "Sell"
ORDERTYPE_SHORT = "Short"
ORDERTYPE_COVER = "Cover"

#Feedback
FEEDBACK_LIMITORDERSENT = "Order sent"
FEEDBACK_STOPORDERBURIED = "Stop order buried"
FEEDBACK_ORDERFAILURE = "Failure to send or bury the order!"