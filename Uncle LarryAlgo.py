//@version=5
strategy("Uncle Larry", overlay=true, pyramiding=0)

//=============================================================================
// 1) SESSION LOGIC (Asian, London, and New York Sessions)
//=============================================================================
asianStartHour = input.int(0, "Asian Start Hour")       // Default: Midnight
asianEndHour   = input.int(6, "Asian End Hour")         // Default: 6 AM
londonStartHour = input.int(2, "London Start Hour")     // Default: 2 AM
nyStartHour     = input.int(11, "New York Start Hour")  // Default: 11 AM
nyEndHour       = input.int(16, "New York End Hour")    // Default: 4 PM

f_inSession(_t) =>
    (hour(_t) >= asianStartHour and hour(_t) < asianEndHour)
    (hour(_t) >= londonStartHour and hour(_t) < nyEndHour)

inSession = f_inSession(time)

//=============================================================================
// 2) FAIR VALUE GAP (Looser Condition)
//=============================================================================
fvgLookback = input.int(1, "FVG Lookback Offset")

bullFVG = low[fvgLookback] >= high[fvgLookback + 1]
bearFVG = high[fvgLookback] <= low[fvgLookback + 1]

//=============================================================================
// 3) MOMENTUM FILTER
//=============================================================================
fastMA = ta.sma(close, 5)
slowMA = ta.sma(close, 20)

momentumLong = ta.crossover(fastMA, slowMA)
momentumShort = ta.crossunder(fastMA, slowMA)

//=============================================================================
// 4) MULTI-TIMEFRAME TREND (30-Minute Confirmation)
//=============================================================================
htfBullTrend = request.security(syminfo.tickerid, "30", close > ta.sma(close, 20))
htfBearTrend = request.security(syminfo.tickerid, "30", close < ta.sma(close, 20))

//=============================================================================
// 5) LIQUIDITY SWEEPS
//=============================================================================
liquiditySweepHigh = high >= ta.highest(high, 10)
liquiditySweepLow = low <= ta.lowest(low, 10)

//=============================================================================
// 6) FIXED $20 RISK CALCULATION
//=============================================================================
riskPerTrade = 20  // Fixed risk per trade in $

pipValueMultiplier = input.float(10, "Pip Value Multiplier (depends on broker)")
f_positionSize(_entry, _stop) =>
    stopLossDistance = math.abs(_entry - _stop)
    pipValue = pipValueMultiplier / syminfo.pointvalue
    riskPerUnit = stopLossDistance * pipValue
    riskPerUnit > 0 ? riskPerTrade / riskPerUnit : na

//=============================================================================
// 7) ENTRY CONDITIONS
//=============================================================================
longCondition = inSession and (bullFVG or liquiditySweepLow or momentumLong) and htfBullTrend
shortCondition = inSession and (bearFVG or liquiditySweepHigh or momentumShort) and htfBearTrend

//=============================================================================
// 8) ENTRY LOGIC WITH DYNAMIC POSITION SIZING
//=============================================================================

// Long Trades
if longCondition
    entryPrice = close
    stopLoss = low[fvgLookback]  // Stop-loss just below the FVG
    takeProfit = entryPrice + (entryPrice - stopLoss) * 1  // 1:1 Take-profit

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

// Short Trades
if shortCondition
    entryPrice = close
    stopLoss = high[fvgLookback]  // Stop-loss just above the FVG
    takeProfit = entryPrice - (stopLoss - entryPrice) * 1  // 1:1 Take-profit

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)
