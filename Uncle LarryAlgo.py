//@version=5
strategy("ICT 4-in-1 with Risk Management", overlay=true, pyramiding=0)

//=============================================================================
// 1) SESSION LOGIC (London and New York Sessions Only)
//=============================================================================
londonStartHour = input.int(2, "London Start Hour")
londonEndHour   = input.int(11, "London End Hour")  // Ends when NY session overlaps
nyStartHour     = input.int(11, "New York Start Hour")
nyEndHour       = input.int(16, "New York End Hour")

// Check if the current hour is within either session
f_inSession(_t) =>
    (hour(_t) >= londonStartHour and hour(_t) < londonEndHour) or
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
// 3) RISK MANAGEMENT CONFIGURATION
//=============================================================================
riskPercent = input.float(2.0, "Risk Per Trade (%)")  // Risk 2% of equity per trade

// Function to calculate position size based on stop-loss
f_positionSize(_entry, _stop) =>
    riskAmount = strategy.equity * (riskPercent / 100)
    distanceToSL = math.abs(_entry - _stop)
    distanceToSL > 0 ? (riskAmount / distanceToSL) : na

//=============================================================================
// 4) SUPPORT/RESISTANCE FOR TAKE-PROFIT
//=============================================================================
// Find the nearest swing high/low within a lookback period
f_findSwingHigh(_lookback) =>
    var float highest = na
    for i = 1 to _lookback
        if high[i] > highest or na(highest)
            highest := high[i]
    highest

f_findSwingLow(_lookback) =>
    var float lowest = na
    for i = 1 to _lookback
        if low[i] < lowest or na(lowest)
            lowest := low[i]
    lowest

swingLookback = input.int(10, "Swing High/Low Lookback Bars")  // Lookback for TP targets

//=============================================================================
// 5) ENTRY CONDITIONS WITH STOP/TP LOGIC
//=============================================================================
if inSession
    // LONG CONDITION: Bullish FVG
    if bullFVG
        entryPrice   = close
        stopLoss     = c2low  // Just below the FVG
        takeProfit   = f_findSwingHigh(swingLookback)  // Next resistance level
        positionSize = f_positionSize(entryPrice, stopLoss)
        if not na(positionSize)
            strategy.entry("Long", strategy.long, qty=positionSize)
            strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

    // SHORT CONDITION: Bearish FVG
    if bearFVG
        entryPrice   = close
        stopLoss     = c2high  // Just above the FVG
        takeProfit   = f_findSwingLow(swingLookback)  // Next support level
        positionSize = f_positionSize(entryPrice, stopLoss)
        if not na(positionSize)
            strategy.entry("Short", strategy.short, qty=positionSize)
            strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)
