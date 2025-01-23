//@version=5
strategy("ShortyV2", overlay=true, pyramiding=1)

// === INPUT PARAMETERS ===
// Common Parameters
initial_balance = input.float(2000, title="Starting Balance", group="Common Settings")
max_daily_risk_pct = input.float(5, title="Max Daily Risk (%)", group="Common Settings")  // Conservative daily risk cap
max_risk_per_trade_pct = input.float(1, title="Max Risk Per Trade (%)", group="Common Settings")  // Reduced risk per trade

// ATR Settings
atr_length = input.int(14, title="ATR Length", group="Common Settings")
atr_multiplier_crypto = input.float(2.0, title="Crypto Multiplier", group="Common Settings")
atr_multiplier_forex = input.float(1.0, title="Forex Multiplier", group="Common Settings")
atr_multiplier_futures = input.float(1.5, title="Futures Multiplier", group="Common Settings")

// Profit-Based Trailing Stop Settings
trail_profit_activation = input.float(0.5, title="Trailing Activation (% of Target Profit)", group="Trailing Stop Loss")
trail_stop_offset_pct = input.float(0.3, title="Trailing Stop Offset (% of Profit)", group="Trailing Stop Loss")

// Asset Class Selector
asset_class = input.string("Forex", title="Asset Class", options=["Crypto", "Forex", "Futures"], group="Common Settings")

// === VARIABLES ===
var float daily_loss = 0.0  // Track daily loss
current_equity = strategy.equity  // Dynamic equity for compounding

// Calculate Risk and Daily Loss Cap
max_risk_per_trade = (max_risk_per_trade_pct / 100) * current_equity
max_daily_risk = (max_daily_risk_pct / 100) * current_equity

// Calculate ATR
atr = ta.atr(atr_length)

// Adjust ATR for Asset Class
asset_multiplier = asset_class == "Crypto" ? atr_multiplier_crypto : 
                   asset_class == "Forex"  ? atr_multiplier_forex : 
                   atr_multiplier_futures

adjusted_atr = atr * asset_multiplier

// === STRATEGY 1: Fibonacci Power of 3 Short ===
// Fibonacci Levels Calculation
high_price_power = ta.highest(high, 10)  // Lookback period for impulse high
low_price_power = ta.lowest(low, 10)    // Lookback period for impulse low
price_range_power = high_price_power - low_price_power
fib_level_618_power = low_price_power + (price_range_power * 0.618)

// Short Setup: Price moves above Fibonacci level and returns inside
is_downtrend = ta.highest(high, 50) > ta.lowest(low, 50) and close < ta.sma(close, 50)  // Downtrend based on lower highs and SMA
short_condition_fib_power = is_downtrend and high > fib_level_618_power and close < fib_level_618_power

// Position Sizing for Short
stop_loss_distance = math.max(math.abs(close - high_price_power), 0.0001)  // Stop-loss distance
pip_value = asset_class == "Forex" ? 0.0001 : 1.0  // Adjust pip value for Forex
position_size_short_power = max_risk_per_trade / (stop_loss_distance / pip_value)

// Cap Position Size
position_size_short_power := math.min(position_size_short_power, max_risk_per_trade / adjusted_atr)

// Execute Short Trade with Trailing Stop
if short_condition_fib_power and daily_loss < max_daily_risk
    strategy.entry("FibShort", strategy.short, qty=position_size_short_power)
    short_target = low_price_power - (price_range_power * 0.618)
    trail_activation = short_target * trail_profit_activation
    trail_offset = trail_activation * trail_stop_offset_pct
    strategy.exit("Short TP", from_entry="FibShort", trail_offset=trail_offset, limit=short_target)

// Plot labels only for executed trades
if strategy.opentrades > 0
    label.new(bar_index, high, text="Short", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)
