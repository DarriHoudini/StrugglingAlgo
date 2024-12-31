//@version=5
strategy("ICT Strategy with Fibonacci TP Levels", overlay=true, pyramiding=0)

//=============================================================================
// 1) SESSION LOGIC (Asian, London, and New York Sessions)
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
// 2) RECENT SWING HIGH/LOW LOGIC
//=============================================================================
lookbackPeriod = input.int(15, "Swing Lookback Period")
recentHigh = ta.highest(high, lookbackPeriod)
recentLow = ta.lowest(low, lookbackPeriod)

//=============================================================================
// 3) FIBONACCI EXTENSIONS FOR TAKE-PROFIT
//=============================================================================
// Define Fibonacci extension levels as numerical inputs
fibLevel1 = input.float(1.0, "Fibonacci Level 1")
fibLevel2 = input.float(1.618, "Fibonacci Level 2")
fibLevel3 = input.float(2.0, "Fibonacci Level 3")

// Calculate Fibonacci-based take-profit levels
priceRange = recentHigh - recentLow
fibTP1 = recentHigh + priceRange * fibLevel1
fibTP2 = recentHigh + priceRange * fibLevel2
fibTP3 = recentHigh + priceRange * fibLevel3

// For shorts, invert the levels
fibTP1Short = recentLow - priceRange * fibLevel1
fibTP2Short = recentLow - priceRange * fibLevel2
fibTP3Short = recentLow - priceRange * fibLevel3

//=============================================================================
// 4) ATR FOR ADDITIONAL STOP BUFFER
//=============================================================================
atrLength = input.int(14, "ATR Length")
atrMultiplier = input.float(1.5, "ATR Stop Buffer Multiplier")
atrValue = ta.atr(atrLength)

//=============================================================================
// 5) FIXED $20 RISK CALCULATION
//=============================================================================
riskPerTrade = 20  // Fixed risk per trade in $
pipValueMultiplier = input.float(10, "Pip Value Multiplier (depends on broker)")
f_positionSize(_entry, _stop) =>
    stopLossDistance = math.abs(_entry - _stop)
    pipValue = pipValueMultiplier / syminfo.pointvalue
    riskPerUnit = stopLossDistance * pipValue
    riskPerUnit > 0 ? riskPerTrade / riskPerUnit : na

//=============================================================================
// 6) ENTRY CONDITIONS
//=============================================================================
bullCondition = close > ta.sma(close, 20) and ta.crossover(close, ta.sma(close, 5))
bearCondition = close < ta.sma(close, 20) and ta.crossunder(close, ta.sma(close, 5))

longCondition = inSession and bullCondition
shortCondition = inSession and bearCondition

//=============================================================================
// 7) ENTRY LOGIC WITH FIBONACCI TAKE-PROFIT LEVELS
//=============================================================================

// Long Trades
if longCondition
    entryPrice = close
    stopLoss = recentLow - (atrValue * atrMultiplier)  // Below recent low with ATR buffer
    takeProfit1 = fibTP1  // First Fibonacci extension level
    takeProfit2 = fibTP2  // Second Fibonacci extension level

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP1/SL", from_entry="Long", stop=stopLoss, limit=takeProfit1)
        strategy.exit("Long TP2/SL", from_entry="Long", stop=stopLoss, limit=takeProfit2)

// Short Trades
if shortCondition
    entryPrice = close
    stopLoss = recentHigh + (atrValue * atrMultiplier)  // Above recent high with ATR buffer
    takeProfit1 = fibTP1Short  // First Fibonacci extension level
    takeProfit2 = fibTP2Short  // Second Fibonacci extension level

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP1/SL", from_entry="Short", stop=stopLoss, limit=takeProfit1)
        strategy.exit("Short TP2/SL", from_entry="Short", stop=stopLoss, limit=takeProfit2)

