//@version=5
strategy("ICT + SMB + HitchHiker Scalp - London & New York Only", overlay=true, pyramiding=3)

//=============================================================================
// 1) ACCOUNT & RISK SETTINGS
//=============================================================================
accountBalance = 2000  
riskPerTrade = 20      
maxTrades = 3          

//=============================================================================
// 2) SESSION LOGIC (London & New York Sessions Only)
//=============================================================================
londonStart = timestamp(year(time), month(time), dayofmonth(time), 2, 00)   // London Open
londonEnd = timestamp(year(time), month(time), dayofmonth(time), 11, 00)    // London Close
nyStart = timestamp(year(time), month(time), dayofmonth(time), 11, 00)      // New York Open
nyEnd = timestamp(year(time), month(time), dayofmonth(time), 16, 00)        // New York Close

inSession = (time >= londonStart and time <= londonEnd) or (time >= nyStart and time <= nyEnd)

//=============================================================================
// 3) ATR-BASED STOP-LOSS & TAKE-PROFIT
//=============================================================================
atrLength = input.int(14, "ATR Length")
atrStopMultiplier = input.float(1.5, "ATR Stop Loss Multiplier")  
atrTPMultiplier = input.float(4.0, "ATR Take Profit Multiplier")  
atrValue = ta.atr(atrLength)

//=============================================================================
// 4) EMA/VWAP CONFIRMATION
//=============================================================================
ema9 = ta.ema(close, 9)
vwap = ta.vwap(close)

// Check for EMA 9 crossing VWAP
emaUpCross = ta.crossover(ema9, vwap)
emaDownCross = ta.crossunder(ema9, vwap)

//=============================================================================
// 5) LIQUIDITY GRAB DETECTION (Touch and Go Confirmation)
//=============================================================================
lookbackSwing = input.int(15, "Liquidity Grab Lookback Period")
recentHigh = ta.highest(high, lookbackSwing)
recentLow = ta.lowest(low, lookbackSwing)

wickThreshold = input.float(0.15, "Wick % for Rejection")  
candleRange = high - low
upperWick = high - close
lowerWick = close - low

liquidityGrabHigh = high >= recentHigh and (upperWick / candleRange) > wickThreshold
liquidityGrabLow = low <= recentLow and (lowerWick / candleRange) > wickThreshold

//=============================================================================
// 6) VOLUME CONFIRMATION
//=============================================================================
volCurrent = ta.sma(volume, 5)  
volPrev = ta.sma(volume, 10)   

volumeIncreasing = volCurrent >= volPrev

//=============================================================================
// 7) HITCHHIKER SCALP LOGIC (Adding to Existing Strategy)
//=============================================================================
// Define price range high and low within consolidation
consolidationLookback = input.int(15, "Consolidation Lookback Period")
consolidationHigh = ta.highest(high, consolidationLookback)
consolidationLow = ta.lowest(low, consolidationLookback)

// Check if consolidation is in upper 1/3 of the day's range
dayHigh = ta.highest(high, 30)  
dayLow = ta.lowest(low, 30)  
upperThird = dayLow + ((dayHigh - dayLow) * 0.67)  

validConsolidation = consolidationLow > upperThird

// Entry Trigger: 1-Min Breakout of Consolidation
hitchHikerBreakout = high > consolidationHigh

//=============================================================================
// 8) ENTRY CONDITIONS (Combining Both Strategies)
//=============================================================================

// Fashionably Late Scalp Entry Conditions
bullConditionFLS = emaUpCross and (liquidityGrabLow or volumeIncreasing)
bearConditionFLS = emaDownCross and (liquidityGrabHigh or volumeIncreasing)

// HitchHiker Scalp Entry Conditions
bullConditionHHS = hitchHikerBreakout and validConsolidation
bearConditionHHS = hitchHikerBreakout and validConsolidation

// Final Conditions (Either Strategy Can Trigger a Trade)
longCondition = inSession and (bullConditionFLS or bullConditionHHS)
shortCondition = inSession and (bearConditionFLS or bearConditionHHS)

//=============================================================================
// 9) POSITION SIZING FUNCTION (Margin-Based Risk of $20 Per Trade)
//=============================================================================
pipValueMultiplier = input.float(10, "Pip Value Multiplier (depends on broker)")

f_positionSize(_entry, _stop) =>
    stopLossDistance = math.abs(_entry - _stop)
    pipValue = pipValueMultiplier / syminfo.pointvalue
    riskPerUnit = stopLossDistance * pipValue
    riskPerUnit > 0 ? riskPerTrade / riskPerUnit : na

currentOpenTrades = strategy.opentrades

//=============================================================================
// 10) TRADE EXECUTION
//=============================================================================

// Long Entry (Fashionably Late or HitchHiker)
if longCondition and currentOpenTrades < maxTrades
    entryPrice = close
    stopLoss = math.min(low - (atrValue * atrStopMultiplier), consolidationLow - 0.02)  
    takeProfit = entryPrice + (atrValue * atrTPMultiplier)  

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Long", strategy.long, qty=positionSize)
        strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)

// Short Entry (Fashionably Late or HitchHiker)
if shortCondition and currentOpenTrades < maxTrades
    entryPrice = close
    stopLoss = math.max(high + (atrValue * atrStopMultiplier), consolidationHigh + 0.02)  
    takeProfit = entryPrice - (atrValue * atrTPMultiplier)  

    positionSize = f_positionSize(entryPrice, stopLoss)
    if not na(positionSize) and positionSize > 0
        strategy.entry("Short", strategy.short, qty=positionSize)
        strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)
