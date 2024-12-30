//@version=5
strategy("ICT 4-in-1 with Clean Entries", overlay=true, pyramiding=0)

//=============================================================================
// 1) SESSION LOGIC (London and New York Sessions Only)
//=============================================================================
londonStartHour = input.int(2, "London Start Hour")
londonEndHour   = input.int(11, "London End Hour")  // Ends when NY session overlaps
nyStartHour     = input.int(11, "New York Start Hour")
nyEndHour       = input.int(16, "New York End Hour")

// Check if the current hour is within either session
f_inSession(_t) =>
    (hour(_t) >= londonStartHour and hour(_t) < londonEndHour)
    (hour(_t) >= nyStartHour and hour(_t) < nyEndHour)

inSession = f_inSession(time)

//=============================================================================
// 2) FAIR VALUE GAP (Looser Condition)
//=============================================================================
fvgLookback = input.int(1, "FVG lookback offset")

c1high = high[fvgLookback + 1]
c1low  = low[fvgLookback + 1]
c2high = high[fvgLookback]
c2low  = low[fvgLookback]
c3high = high[fvgLookback - 1]
c3low  = low[fvgLookback - 1]

// Looser conditions: only require gap vs. previous OR next candle
bullFVG = (c2low > c1high) or (c2low > c3high)
bearFVG = (c2high < c1low) or (c2high < c3low)

//=============================================================================
// 3) OTE (Optional Filter)
//=============================================================================
oteLookback = input.int(5, "OTE Swing Lookback Bars")
oteMin = 0.38  // Broadened to 38%
oteMax = 1.00  // Extended to 100%

// Find the recent swing high and swing low
swingHigh = ta.highest(high, oteLookback)
swingLow  = ta.lowest(low, oteLookback)

// Calculate OTE zone
fib38 = swingLow + (swingHigh - swingLow) * oteMin
fib100 = swingLow + (swingHigh - swingLow) * oteMax

// Check if price is in the OTE zone
inOTE = close >= fib38 and close <= fib100

//=============================================================================
// 4) ENTRY CONDITIONS
//=============================================================================
// Combine FVG, BOS, and OTE for long and short conditions
bullBOS = not na(swingHigh) and close > swingHigh
bearBOS = not na(swingLow) and close < swingLow

longCondition  = inSession and (bullFVG or bullBOS) and (inOTE or not inOTE)
shortCondition = inSession and (bearFVG or bearBOS) and (inOTE or not inOTE)

//=============================================================================
// 5) RISK MANAGEMENT
//=============================================================================
riskPercent = input.float(2.0, "Risk Per Trade (%)")

// Calculate position size based on risk and stop-loss distance
f_positionSize(_entry, _stop) =>
    riskAmount = strategy.equity * (riskPercent / 100)
    distanceToSL = math.abs(_entry - _stop)
    distanceToSL > 0 ? (riskAmount / distanceToSL) : na

//=============================================================================
// 6) ENTRY LOGIC
//=============================================================================
if longCondition
    entryPrice = close
    stopLoss = c2low  // Stop-loss just below the FVG
    takeProfit = swingHigh  // Take-profit at next resistance
    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize)
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

if shortCondition
    entryPrice = close
    stopLoss = c2high  // Stop-loss just above the FVG
    takeProfit = swingLow  // Take-profit at next support
    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize)
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)

//=============================================================================
// CLEANED VISUALIZATION
//=============================================================================
// All visual elements like Fibonacci levels and OTE highlights have been removed.
