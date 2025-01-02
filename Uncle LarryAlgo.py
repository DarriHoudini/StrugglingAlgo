//@version=5
strategy("ICT Strategy with ATR Stop Loss & TP - $20 Risk", overlay=true, pyramiding=3)

//=============================================================================
// 1) ACCOUNT & RISK SETTINGS
//=============================================================================
accountBalance = 2000  // Account balance in USD
riskPerTrade = 20      // Fixed risk per trade in $
maxTrades = 3          // Maximum number of open trades

//=============================================================================
// 2) SESSION LOGIC (Asian, London, and New York Sessions)
//=============================================================================
asianStartHour = input.int(0, "Asian Start Hour")
asianEndHour   = input.int(6, "Asian End Hour")
londonStartHour = input.int(2, "London Start Hour")
nyStartHour     = input.int(11, "New York Start Hour")
nyEndHour       = input.int(16, "New York End Hour")

f_inSession(_t) =>
    (hour(_t) >= asianStartHour and hour(_t) < asianEndHour)
    (hour(_t) >= londonStartHour and hour(_t) < nyEndHour)

inSession = f_inSession(time)

//=============================================================================
// 3) ATR FOR STOP-LOSS AND TAKE-PROFIT
//=============================================================================
atrLength = input.int(14, "ATR Length")
atrStopMultiplier = input.float(2.0, "ATR Stop Loss Multiplier")
atrTPMultiplier = input.float(4.0, "ATR Take Profit Multiplier")
atrValue = ta.atr(atrLength)

//=============================================================================
// 4) POSITION SIZING
//=============================================================================
pipValueMultiplier = input.float(10, "Pip Value Multiplier (depends on broker)")
f_positionSize(_entry, _stop) =>
    stopLossDistance = math.abs(_entry - _stop)
    pipValue = pipValueMultiplier / syminfo.pointvalue
    riskPerUnit = stopLossDistance * pipValue
    riskPerUnit > 0 ? riskPerTrade / riskPerUnit : na

//=============================================================================
// 5) ENTRY CONDITIONS
//=============================================================================
bullCondition = close > ta.sma(close, 20) and ta.crossover(close, ta.sma(close, 5))
bearCondition = close < ta.sma(close, 20) and ta.crossunder(close, ta.sma(close, 5))

longCondition = inSession and bullCondition
shortCondition = inSession and bearCondition

//=============================================================================
// 6) ENTRY LOGIC WITH RISK MANAGEMENT
//=============================================================================
currentOpenTrades = strategy.opentrades

// Long Trades
if longCondition and currentOpenTrades < maxTrades
    entryPrice = close
    stopLoss = entryPrice - (atrValue * atrStopMultiplier)  // 2x ATR below entry
    takeProfit = entryPrice + (atrValue * atrTPMultiplier)  // 4x ATR above entry

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

// Short Trades
if shortCondition and currentOpenTrades < maxTrades
    entryPrice = close
    stopLoss = entryPrice + (atrValue * atrStopMultiplier)  // 2x ATR above entry
    takeProfit = entryPrice - (atrValue * atrTPMultiplier)  // 4x ATR below entry

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)
