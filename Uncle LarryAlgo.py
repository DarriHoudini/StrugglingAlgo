//@version=5
strategy("Uncle Larry V3)", overlay=true, default_qty_type=strategy.cash, default_qty_value=20, pyramiding=1)

// === Inputs
riskPerTrade = input.float(20, "Risk Per Trade ($)")
atrLength = input.int(14, "ATR Length")
structureLookback = input.int(10, "Structure Lookback")
atrStopMultiplier = input.float(1.5, "Stop Loss Multiplier")
atrTPMultiplier = input.float(4.0, "Take Profit Multiplier")
pipValueMultiplier = input.float(10, "Pip Value Multiplier")

// === Sessions: London and New York
londonStart = timestamp("GMT+0", year(time), month(time), dayofmonth(time), 2, 0)
londonEnd   = timestamp("GMT+0", year(time), month(time), dayofmonth(time), 11, 0)
nyStart     = timestamp("GMT+0", year(time), month(time), dayofmonth(time), 11, 0)
nyEnd       = timestamp("GMT+0", year(time), month(time), dayofmonth(time), 16, 0)

inLondonSession = time >= londonStart and time < londonEnd
inNYSession     = time >= nyStart and time < nyEnd

// === Track trades per session
var int lastLondonTradeBar = na
var int lastNYTradeBar = na

tradedLondon = inLondonSession and (na(lastLondonTradeBar) or lastLondonTradeBar < londonStart)
tradedNY = inNYSession and (na(lastNYTradeBar) or lastNYTradeBar < nyStart)

// === ATR
atr = ta.atr(atrLength)

// === BOS Detection Only (Volume removed)
prevHigh = ta.highest(high[1], structureLookback)
prevLow = ta.lowest(low[1], structureLookback)
bosUp = close > prevHigh
bosDown = close < prevLow

// === Position Sizing
f_positionSize(_entry, _stop) =>
    dist = math.abs(_entry - _stop)
    pipValue = pipValueMultiplier / syminfo.pointvalue
    riskPerUnit = dist * pipValue
    riskPerUnit > 0 ? riskPerTrade / riskPerUnit : na

// === Long Trade
if bosUp and (tradedLondon or tradedNY)
    entryPrice = close
    stopLoss = close - atr * atrStopMultiplier
    takeProfit = close + atr * atrTPMultiplier
    size = f_positionSize(entryPrice, stopLoss)
    if not na(size) and size > 0
        strategy.entry("Long", strategy.long, qty=size)
        strategy.exit("Long Exit", from_entry="Long", stop=stopLoss, limit=takeProfit)
        if inLondonSession
            lastLondonTradeBar := bar_index
        if inNYSession
            lastNYTradeBar := bar_index

// === Short Trade
if bosDown and (tradedLondon or tradedNY)
    entryPrice = close
    stopLoss = close + atr * atrStopMultiplier
    takeProfit = close - atr * atrTPMultiplier
    size = f_positionSize(entryPrice, stopLoss)
    if not na(size) and size > 0
        strategy.entry("Short", strategy.short, qty=size)
        strategy.exit("Short Exit", from_entry="Short", stop=stopLoss, limit=takeProfit)
        if inLondonSession
            lastLondonTradeBar := bar_index
        if inNYSession
            lastNYTradeBar := bar_index

