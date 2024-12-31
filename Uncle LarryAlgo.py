//@version=5
strategy("ICT Strategy with Adjusted Confirmation", overlay=true, pyramiding=0)

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

// Broadened FVG conditions
bullFVG = low[fvgLookback] >= high[fvgLookback + 1]
bearFVG = high[fvgLookback] <= low[fvgLookback + 1]

//=============================================================================
// 3) MOMENTUM FILTER (Optional)
//=============================================================================
fastMA = ta.sma(close, 5)
slowMA = ta.sma(close, 20)

momentumLong = ta.crossover(fastMA, slowMA) or true
momentumShort = ta.crossunder(fastMA, slowMA) or true

//=============================================================================
// 4) MULTI-TIMEFRAME TREND (30-Minute Confirmation)
//=============================================================================
htfBullTrend = request.security(syminfo.tickerid, "30", close > ta.sma(close, 20))
htfBearTrend = request.security(syminfo.tickerid, "30", close < ta.sma(close, 20))

//=============================================================================
// 5) LIQUIDITY SWEEPS
//=============================================================================
liquiditySweepHigh = high >= ta.highest(high, 10)  // Broader lookback for highs
liquiditySweepLow = low <= ta.lowest(low, 10)  // Broader lookback for lows

//=============================================================================
// 6) ENTRY CONDITIONS
//=============================================================================
// Use OR conditions to broaden trade setups
longCondition = inSession and (bullFVG or liquiditySweepLow or momentumLong) and htfBullTrend
shortCondition = inSession and (bearFVG or liquiditySweepHigh or momentumShort) and htfBearTrend

//=============================================================================
// 7) RISK MANAGEMENT
//=============================================================================
riskPercent = input.float(2.0, "Risk Per Trade (%)")

// Calculate position size based on risk and stop-loss distance
f_positionSize(_entry, _stop) =>
    riskAmount = strategy.equity * (riskPercent / 100)
    distanceToSL = math.abs(_entry - _stop)
    distanceToSL > 0 ? (riskAmount / distanceToSL) : na

//=============================================================================
// 8) ENTRY LOGIC
//=============================================================================
if longCondition
    entryPrice = close
    stopLoss = low[fvgLookback]  // Stop-loss just below the FVG
    takeProfit = entryPrice + (entryPrice - stopLoss) * 2  // 2R Take-profit
    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize)
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

if shortCondition
    entryPrice = close
    stopLoss = high[fvgLookback]  // Stop-loss just above the FVG
    takeProfit = entryPrice - (stopLoss - entryPrice) * 2  // 2R Take-profit
    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize)
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)

//=============================================================================
// 9) PLOTTING & DEBUGGING
//=============================================================================
// No additional visual elements for a clean chart

