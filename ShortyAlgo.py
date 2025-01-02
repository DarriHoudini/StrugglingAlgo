//@version=5
strategy("Turtle Soup Shorting", overlay=true, pyramiding=0)

// Input Parameters
lookback_high = input(20, title="Lookback Period for High")
risk_per_trade = input.float(40, title="Risk Per Trade ($)", minval=1)
atr_multiplier = input.float(1.5, title="ATR Multiplier for Stop-Loss")
zone_buffer = input.float(0.0001, title="Buffer Above/Below Zone")

// Calculations
high_level = ta.highest(high, lookback_high)
low_level = ta.lowest(low, lookback_high)
atr = ta.atr(14)

// Supply and Demand Zones
supply_zone = ta.valuewhen(high == high_level, high, 0)
demand_zone = ta.valuewhen(low == low_level, low, 0)

// Short Setup: Price breaks above the high level and reverses
short_condition = high > high_level and close < high_level

// Stop-Loss and Position Sizing for Shorts
stop_loss_short = supply_zone + zone_buffer
risk_per_unit_short = stop_loss_short - close
position_size_short = risk_per_trade / math.abs(risk_per_unit_short)

// Long Setup: Price breaks below the low level and reverses
long_condition = low < low_level and close > low_level

// Stop-Loss and Position Sizing for Longs
stop_loss_long = demand_zone - zone_buffer
risk_per_unit_long = close - stop_loss_long
position_size_long = risk_per_trade / math.abs(risk_per_unit_long)

// Execute Short Trade
if short_condition
    entryPrice = close
    takeProfit1 = supply_zone - (atr * atr_multiplier)  // First Fibonacci-like level
    takeProfit2 = supply_zone - 2 * (atr * atr_multiplier)  // Second level
    
    strategy.entry("TurtleSoupShort", strategy.short, qty=position_size_short)
    strategy.exit("Short TP1", from_entry="TurtleSoupShort", stop=stop_loss_short, limit=takeProfit1)
    strategy.exit("Short TP2", from_entry="TurtleSoupShort", stop=stop_loss_short, limit=takeProfit2)

// Execute Long Trade
if long_condition
    entryPrice = close
    takeProfit1 = demand_zone + (atr * atr_multiplier)  // First Fibonacci-like level
    takeProfit2 = demand_zone + 2 * (atr * atr_multiplier)  // Second level
    
    strategy.entry("TurtleSoupLong", strategy.long, qty=position_size_long)
    strategy.exit("Long TP1", from_entry="TurtleSoupLong", stop=stop_loss_long, limit=takeProfit1)
    strategy.exit("Long TP2", from_entry="TurtleSoupLong", stop=stop_loss_long, limit=takeProfit2)

// Highlight Trades with Labels and Arrows
if short_condition
    label.new(bar_index, high, text="Short", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.normal)
if long_condition
    label.new(bar_index, low, text="Long", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.normal)

