//@version=5
strategy("Fibonacci Power of 3 Short", overlay=true, pyramiding=1)

// Input Parameters
risk_per_trade = input.float(40, title="Risk Per Trade ($)", minval=1)
fib_level_high = input.float(1.618, title="Fibonacci Extension Level High")
fib_level_mid = input.float(1.0, title="Fibonacci Extension Level Mid")
fib_level_low = input.float(0.618, title="Fibonacci Extension Level Low")

// Market Structure & Trend Detection
is_downtrend = ta.highest(high, 50) > ta.lowest(low, 50) and close < ta.sma(close, 50)  // Downtrend based on lower highs and SMA

// Fibonacci Levels Calculation
high_price = ta.highest(high, 10)  // Lookback period for impulse high
low_price = ta.lowest(low, 10)    // Lookback period for impulse low
price_range = high_price - low_price
fib_level_382 = low_price + (price_range * 0.382)
fib_level_618 = low_price + (price_range * 0.618)

// Short Setup: Price moves above Fibonacci level and returns inside
short_condition = is_downtrend and high > fib_level_618 and close < fib_level_618

// Stop-Loss and Position Sizing for Shorts
stop_loss_short = high_price  // Most recent swing high
risk_per_unit_short = stop_loss_short - close
position_size_short = risk_per_trade / math.abs(risk_per_unit_short)

// Execute Short Trade
if short_condition
    entryPrice = close
    takeProfit1 = low_price - (price_range * 0.27)  // First take-profit below swing low
    takeProfit2 = low_price - (price_range * 0.618)  // Second take-profit further down
    
    strategy.entry("FibShort", strategy.short, qty=position_size_short)
    strategy.exit("Short TP1", from_entry="FibShort", stop=stop_loss_short, limit=takeProfit1)
    strategy.exit("Short TP2", from_entry="FibShort", stop=stop_loss_short, limit=takeProfit2)

// Highlight Trades with Labels and Arrows
if short_condition
    label.new(bar_index, high, text="Short", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.normal)
    line.new(x1=bar_index, y1=high, x2=bar_index, y2=stop_loss_short, color=color.red, width=2, style=line.style_solid)

// Plot Fibonacci Levels
plot(fib_level_382, color=color.orange, title="Fib Level 38.2%")
plot(fib_level_618, color=color.green, title="Fib Level 61.8%")
plot(high_price, color=color.red, title="Swing High")
plot(low_price, color=color.blue, title="Swing Low")
