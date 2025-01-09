//@version=5
strategy("StruggleAlgoV2)", overlay=true, pyramiding=1)

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
position_size_short_power = max_risk_per_trade / (adjusted_atr * 10)

// Execute Short Trade
if short_condition_fib_power and daily_loss < max_daily_risk
    strategy.entry("FibShort", strategy.short, qty=position_size_short_power)
    strategy.exit("Short TP1", from_entry="FibShort", stop=high_price_power, limit=low_price_power - (price_range_power * 0.27))
    strategy.exit("Short TP2", from_entry="FibShort", stop=high_price_power, limit=low_price_power - (price_range_power * 0.618))

// Highlight Short Entry
if short_condition_fib_power
    label.new(bar_index, high, text="Short", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)

// === STRATEGY 2: Enhanced SMA & Fibonacci Strategy ===
// Fibonacci Levels
high_price_sma = ta.highest(high, 10)
low_price_sma = ta.lowest(low, 10)
fib_level_382_sma = low_price_sma + (high_price_sma - low_price_sma) * 0.382
fib_level_50_sma = low_price_sma + (high_price_sma - low_price_sma) * 0.5
fib_level_618_sma = low_price_sma + (high_price_sma - low_price_sma) * 0.618
fib_level_786_sma = low_price_sma + (high_price_sma - low_price_sma) * 0.786
fib_target_sma = high_price_sma + (high_price_sma - low_price_sma) * 0.27

// Detect SMA Cross
len1 = input.int(5, title="SMA Length 1", group="Enhanced SMA & Fibonacci")
len2 = input.int(15, title="SMA Length 2", group="Enhanced SMA & Fibonacci")
ema1 = ta.sma(close, len1)
ema2 = ta.sma(close, len2)
buy_tr = ta.crossover(ema1, ema2)
sell_tr = ta.crossunder(ema1, ema2)

// Detect Impulse Move
impulse_detected_long_382 = close > fib_level_382_sma and close < fib_level_50_sma and buy_tr
impulse_detected_long_618 = close > fib_level_50_sma and close < fib_level_786_sma and buy_tr
impulse_detected_short_382 = close < fib_level_382_sma and close > fib_level_50_sma and sell_tr
impulse_detected_short_618 = close < fib_level_50_sma and close > fib_level_786_sma and sell_tr

// Position Sizing for SMA Strategy
position_size_long = max_risk_per_trade / (adjusted_atr * 10)
position_size_short_sma = max_risk_per_trade / (adjusted_atr * 10)

// Track Daily Loss
if daily_loss >= max_daily_risk
    strategy.close_all(comment="Max daily risk reached")

// Entry and Exit Conditions
if impulse_detected_long_382 and daily_loss < max_daily_risk
    strategy.entry("Long_382", strategy.long, qty=position_size_long, comment="Long_382")
    strategy.exit("TakeProfit_382", "Long_382", limit=fib_target_sma, stop=low_price_sma)
    label.new(bar_index, low, text="Long_382", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)

if impulse_detected_long_618 and daily_loss < max_daily_risk
    strategy.entry("Long_618", strategy.long, qty=position_size_long, comment="Long_618")
    strategy.exit("TakeProfit_618", "Long_618", limit=fib_target_sma, stop=low_price_sma)
    label.new(bar_index, low, text="Long_618", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)

if impulse_detected_short_382 and daily_loss < max_daily_risk
    strategy.entry("Short_382", strategy.short, qty=position_size_short_sma, comment="Short_382")
    strategy.exit("TakeProfit_382", "Short_382", limit=fib_target_sma, stop=high_price_sma)
    label.new(bar_index, high, text="Short_382", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)

if impulse_detected_short_618 and daily_loss < max_daily_risk
    strategy.entry("Short_618", strategy.short, qty=position_size_short_sma, comment="Short_618")
    strategy.exit("TakeProfit_618", "Short_618", limit=fib_target_sma, stop=high_price_sma)
    label.new(bar_index, high, text="Short_618", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)

// === DETERMINE OUTCOME (TP or SL) ===
trade_closed = na(strategy.position_size[1]) and not na(strategy.position_size)  // Detect when trade closes
is_tp = strategy.closedtrades.profit(strategy.closedtrades - 1) > 0
is_sl = strategy.closedtrades.profit(strategy.closedtrades - 1) <= 0

if trade_closed
    if is_tp
        label.new(bar_index, close, text="TP Hit", style=label.style_label_up, color=color.green, textcolor=color.white, size=size.small)
    if is_sl
        label.new(bar_index, close, text="SL Hit", style=label.style_label_down, color=color.red, textcolor=color.white, size=size.small)

