//@version=5
strategy("CRT_Strategy_Debug", overlay=true, pyramiding=1)

// === INPUT PARAMETERS ===
// Common Parameters
starting_balance = input.float(2000, title="Starting Balance", group="Common Settings")
max_daily_risk_pct = input.float(15, title="Max Daily Risk (%)", group="Common Settings")
risk_per_trade_pct = input.float(2, title="Risk per Trade (%)", group="Common Settings")

// ATR Settings
atr_length = input.int(14, title="ATR Length", group="Common Settings")
atr_multiplier = input.float(1.5, title="ATR Multiplier", group="Common Settings")

// === VARIABLES ===
var float max_daily_risk = (max_daily_risk_pct / 100) * starting_balance
risk_per_trade = (risk_per_trade_pct / 100) * starting_balance
var float daily_loss = 0.0  // Track daily loss

// Calculate ATR
atr = ta.atr(atr_length)
adjusted_atr = atr * atr_multiplier

// === CRT Logic ===
// Define Critical Reaction Threshold (CRT) Levels
crt_lookback = input.int(20, title="CRT Lookback Period", group="CRT Settings")
crt_high = ta.highest(high, crt_lookback)  // High of a reaction zone
crt_low = ta.lowest(low, crt_lookback)    // Low of a reaction zone
crt_mid = (crt_high + crt_low) / 2        // Midpoint for reactions

// Debugging flags for conditions
var bool long_debug = false
var bool short_debug = false
var bool long_condition_crt = false
var bool short_condition_crt = false

// Long Condition: Price crosses above CRT low or CRT mid
if low <= crt_low and close > crt_mid
    long_condition_crt := true
else if close > crt_low
    long_debug := true
    long_condition_crt := false

// Short Condition: Price crosses below CRT high or CRT mid
if high >= crt_high and close < crt_mid
    short_condition_crt := true
else if close < crt_high
    short_debug := true
    short_condition_crt := false

// Position Sizing
position_size_crt = risk_per_trade / adjusted_atr

// Entry and Exit Rules
if long_condition_crt and daily_loss < max_daily_risk
    strategy.entry("CRT_Long", strategy.long, qty=position_size_crt, comment="CRT Long")
    strategy.exit("TakeProfit_CRT_Long", "CRT_Long", limit=crt_high, stop=crt_low)
    label.new(bar_index, low, text="CRT Long", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)

if short_condition_crt and daily_loss < max_daily_risk
    strategy.entry("CRT_Short", strategy.short, qty=position_size_crt, comment="CRT Short")
    strategy.exit("TakeProfit_CRT_Short", "CRT_Short", limit=crt_low, stop=crt_high)
    label.new(bar_index, high, text="CRT Short", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)

// Debugging: Add labels for potential trades
if long_debug
    label.new(bar_index, low, text="Long Condition Evaluated", style=label.style_label_up, color=color.yellow, textcolor=color.black, size=size.tiny)

if short_debug
    label.new(bar_index, high, text="Short Condition Evaluated", style=label.style_label_down, color=color.yellow, textcolor=color.black, size=size.tiny)

// === Daily Loss Tracking ===
// Close all trades if daily loss exceeds the max daily risk
if daily_loss >= max_daily_risk
    strategy.close_all(comment="Max daily risk reached")

// === Outcome Detection ===
trade_closed = na(strategy.position_size[1]) and not na(strategy.position_size)  // Detect when trade closes
is_tp = strategy.closedtrades.profit(strategy.closedtrades - 1) > 0
is_sl = strategy.closedtrades.profit(strategy.closedtrades - 1) <= 0

if trade_closed
    if is_tp
        label.new(bar_index, close, text="TP Hit", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)
    if is_sl
        label.new(bar_index, close, text="SL Hit", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)
