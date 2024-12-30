//@version=5
strategy("ICT 4-in-1 Demo - Simplified Sessions (London & NY)", overlay=true, pyramiding=0)

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
// 3) BREAK OF STRUCTURE (Reduced fractal lookback from 10 to 3)
//=============================================================================
fFractalHigh(_i) =>
    high[_i] > high[_i + 1] and high[_i] > high[_i - 1]

fFractalLow(_i) =>
    low[_i] < low[_i + 1] and low[_i] < low[_i - 1]

fractalLookback = input.int(3, "Fractal BOS lookback bars")

var float lastFractalHigh    = na
var float lastFractalLow     = na
var int   lastFractalHighBar = na
var int   lastFractalLowBar  = na

if barstate.isnew
    // fractal high
    for i = 1 to fractalLookback
        if fFractalHigh(i)
            lastFractalHigh    := high[i]
            lastFractalHighBar := bar_index - i
            break
    // fractal low
    for i = 1 to fractalLookback
        if fFractalLow(i)
            lastFractalLow    := low[i]
            lastFractalLowBar := bar_index - i
            break

bullBOS = not na(lastFractalHigh) and (close > lastFractalHigh)
bearBOS = not na(lastFractalLow)  and (close < lastFractalLow)

//=============================================================================
// 4) REMOVE Premium/Discount Requirement for demonstration
//=============================================================================
longCondition  = inSession and (bullFVG or bullBOS)
shortCondition = inSession and (bearFVG or bearBOS)

// Simple example: entry on conditions
if longCondition
    strategy.entry("Long", strategy.long)
    
if shortCondition
    strategy.entry("Short", strategy.short)
