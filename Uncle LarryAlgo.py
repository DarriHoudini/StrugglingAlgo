//@version=5
strategy("ICT Strategy with Native SL/TP", overlay=true, pyramiding=0)

//=============================================================================
// 1) SESSION LOGIC (London and New York Sessions Only)
//=============================================================================
londonStartHour = input.int(2, "London Start Hour")
nyStartHour     = input.int(11, "New York Start Hour")
nyEndHour       = input.int(16, "New York End Hour")

f_inSession(_t) =>
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
// 6) FIXED RISK CALCULATION
//=============================================================================
fixedRisk = 35  // Fixed risk per trade in $
f_positionSize(_entry, _stop) =>
    riskPerUnit = math.abs(_entry - _stop)
    riskPerUnit > 0 ? fixedRisk / riskPerUnit : na

//=============================================================================
// 7) ENTRY CONDITIONS
//=============================================================================
longCondition = inSession and (bullFVG or liquiditySweepLow or momentumLong) and htfBullTrend
shortCondition = inSession and (bearFVG or liquiditySweepHigh or momentumShort) and htfBearTrend

//=============================================================================
// 8) ENTRY LOGIC WITH MULTI-LEVEL TARGETS
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
    takeProfit1 = entryPrice - (stopLoss - entryPrice) * 1  // 1:1 Take-profit
    takeProfit2 = entryPrice - (stopLoss - entryPrice) * 2  // 1:2 Take-profit
    takeProfit3 = entryPrice - (stopLoss - entryPrice) * 3  // 1:3 Take-profit

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Short", strategy.short, qty=positionSize)
        
        // Multi-level exit logic for shorts
        if momentumShort
            strategy.exit("Short TP/SL (1:3)", from_entry="Short", stop=stopLoss, limit=takeProfit3)
        else
            strategy.exit("Short TP/SL (1:1)", from_entry="Short", stop=stopLoss, limit=takeProfit1)

//=============================================================================
// CLEANED VISUALIZATION
//=============================================================================
// Removed custom plot() for Stop-Loss and Take-Profit
