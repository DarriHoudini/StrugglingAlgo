//@version=5
strategy("ICT 4-in-1 Demo (Time Filter, FVG, BOS, Premium/Discount) - Fixed Types", overlay=true)

//=============================================================================
// 1) TIME FILTER (example: "London Session" ~ 2–5 AM exchange time)
//=============================================================================
startHour   = input.int(2,  "Session Start Hour (24h)",   tooltip="e.g., 2 for 2:00 AM")
endHour     = input.int(5,  "Session End Hour (24h)",     tooltip="e.g., 5 for 5:00 AM")
useTimeFilt = input.bool(true, "Use Time Filter?")

f_inSession(_t) =>
    hourInSession = (hour(_t) >= startHour) and (hour(_t) < endHour)
    hourInSession

inSession = useTimeFilt ? f_inSession(time) : true

//=============================================================================
// 2) FAIR VALUE GAP (FVG) DETECTION
//=============================================================================
fvgLookback = input.int(1, "FVG lookback offset", tooltip="How far back the middle candle is")

// Candle references
c1high = high[fvgLookback + 1]
c1low  = low[fvgLookback + 1]
c2high = high[fvgLookback]
c2low  = low[fvgLookback]
c3high = high[fvgLookback - 1]
c3low  = low[fvgLookback - 1]

// Basic bullish FVG
bullFVG  = (c2low > c1high) and (c2low > c3high)
// Basic bearish FVG
bearFVG  = (c2high < c1low) and (c2high < c3low)

//=============================================================================
// 3) BREAK OF STRUCTURE (BOS) via fractals
//=============================================================================
fFractalHigh(_i) =>
    high[_i] > high[_i + 1] and high[_i] > high[_i - 1]

fFractalLow(_i) =>
    low[_i] < low[_i + 1] and low[_i] < low[_i - 1]

// We need `var` with explicit types for variables that start as na
fractalLookback = input.int(10, "Fractal BOS lookback bars")
var float lastFractalHigh    = na
var float lastFractalLow     = na
var int   lastFractalHighBar = na
var int   lastFractalLowBar  = na

if barstate.isnew
    // Find the most recent fractal high within fractalLookback bars
    for i = 1 to fractalLookback
        if fFractalHigh(i)
            lastFractalHigh    := high[i]
            lastFractalHighBar := bar_index - i
            break
    // Find the most recent fractal low within fractalLookback bars
    for i = 1 to fractalLookback
        if fFractalLow(i)
            lastFractalLow    := low[i]
            lastFractalLowBar := bar_index - i
            break

// If close > lastFractalHigh => bullish BOS
bullBOS = not na(lastFractalHigh) and (close > lastFractalHigh)
// If close < lastFractalLow  => bearish BOS
bearBOS = not na(lastFractalLow)  and (close < lastFractalLow)

//=============================================================================
// 4) PREMIUM / DISCOUNT from recent fractal-based swing range
//=============================================================================
var float swingHigh = na
var float swingLow  = na
var float midPoint  = na

if not na(lastFractalHigh) and not na(lastFractalLow)
    // We'll define swingHigh as the higher of the two fractals, swingLow as the lower
    swingHigh := math.max(lastFractalHigh, lastFractalLow)
    swingLow  := math.min(lastFractalHigh, lastFractalLow)
    midPoint  := (swingHigh + swingLow) / 2.0

inDiscount = not na(midPoint) and (close < midPoint)
inPremium  = not na(midPoint) and (close > midPoint)

//=============================================================================
// SIMPLE SAMPLE STRATEGY
//=============================================================================
longCondition  = inSession and inDiscount and (bullFVG or bullBOS)
shortCondition = inSession and inPremium  and (bearFVG or bearBOS)

// We'll just do a simple entry with no stops
if longCondition
    strategy.entry("Long", strategy.long)
    
if shortCondition
    strategy.entry("Short", strategy.short)

//=============================================================================
// PLOTTING & DEBUG
//=============================================================================
plot(midPoint, color=color.gray, linewidth=1, title="Midpoint of fractal range")

plotshape(bullBOS, style=shape.labelup,   color=color.green,  size=size.tiny, title="Bull BOS", text="BOS↑")
plotshape(bearBOS, style=shape.labeldown, color=color.red,    size=size.tiny, title="Bear BOS", text="BOS↓")

plotshape(bullFVG, style=shape.circle, color=color.new(color.lime, 0),   title="Bull FVG", text="FVG↑", location=location.top)
plotshape(bearFVG, style=shape.circle, color=color.new(color.red,  0),   title="Bear FVG", text="FVG↓", location=location.bottom)
