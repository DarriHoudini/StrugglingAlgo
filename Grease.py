//@version=5
strategy("Grease V1", overlay=true, max_bars_back=500)

// ========== SETTINGS ==========
startHour = 0   // 12:00 AM ET
endHour   = 15  // 3:00 PM ET
maxTradesPerDay = 3

initialRisk = 1000.0  // First trade risk ($)
reducedRisk = 250.0   // Risk for second and third trades ($)

// ========== SESSION WINDOW ==========
getCurrentDay() =>
    year * 10000 + month * 100 + dayofmonth

inTimeRange = (hour(time, "America/New_York") >= startHour and hour(time, "America/New_York") < endHour)
currentDay = getCurrentDay()
var int todayTradeCount = 0
var int lastTradeDay = na

if na(lastTradeDay) or currentDay != lastTradeDay
    todayTradeCount := 0
    lastTradeDay := currentDay

// ========== ATR ==========
atrLength = input.int(14, "ATR Length")
atrMult = input.float(1.0, "ATR Multiplier")
atr = ta.atr(atrLength)

// ========== VWAP & EMA ==========
ema9 = ta.ema(close, 9)
vwap = ta.vwap(close)
emaCrossAbove = ta.crossover(ema9, vwap)
emaCrossBelow = ta.crossunder(ema9, vwap)

// ========== TICK VALUE DETECTION ==========
tickValue = syminfo.root == "M6E" ? 1.25 : syminfo.root == "MNQ" ? 0.50 : syminfo.root == "MGC" ? 1.00 : 1.0
pointValue = syminfo.pointvalue
dollarPerPoint = tickValue * pointValue

// ========== RISK ENGINE ==========
var float currentRisk = initialRisk

// ========== SIGNALS ==========
longSignal  = emaCrossAbove
shortSignal = emaCrossBelow
canTrade = inTimeRange and (todayTradeCount < maxTradesPerDay)

// ========== TRADE EXECUTION ==========
if (longSignal and canTrade)
    stopLoss = close - (atr * atrMult)
    takeProfit = close + (atr * atrMult)
    stopDist = close - stopLoss
    positionSize = currentRisk / (stopDist * dollarPerPoint)
    strategy.entry("Long", strategy.long, qty=positionSize)
    strategy.exit("Long TP/SL", from_entry="Long", stop=stopLoss, limit=takeProfit)
    label.new(bar_index, low, "🟢 Buy", style=label.style_label_up)
    todayTradeCount += 1
    currentRisk := reducedRisk

if (shortSignal and canTrade)
    stopLoss = close + (atr * atrMult)
    takeProfit = close - (atr * atrMult)
    stopDist = stopLoss - close
    positionSize = currentRisk / (stopDist * dollarPerPoint)
    strategy.entry("Short", strategy.short, qty=positionSize)
    strategy.exit("Short TP/SL", from_entry="Short", stop=stopLoss, limit=takeProfit)
    label.new(bar_index, high, "🔴 Sell", style=label.style_label_down)
    todayTradeCount += 1
    currentRisk := reducedRisk

