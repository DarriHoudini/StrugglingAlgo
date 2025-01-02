//@version=5
strategy("Enhanced SMA & Fibonacci Strategy with 38.2%", overlay=true, default_qty_type=strategy.percent_of_equity, default_qty_value=2)

// === INPUT PARAMETERS ===
starting_balance = input.float(2000, title="Starting Balance")
max_daily_risk_pct = input.float(15, title="Max Daily Risk (%)")
risk_per_trade_pct = input.float(2, title="Risk per Trade (%)")

// === VARIABLES ===
var float max_daily_risk = (max_daily_risk_pct / 100) * starting_balance
risk_per_trade = (risk_per_trade_pct / 100) * starting_balance
var float daily_loss = 0.0  // Track daily loss

// === SMA PARAMETERS ===
len1 = input.int(5, title="SMA Length 1")
len2 = input.int(15, title="SMA Length 2")

// === FIBONACCI LEVELS ===
high_price = ta.highest(high, 10)  // Lookback period for impulse high
low_price = ta.lowest(low, 10)    // Lookback period for impulse low

fib_level_0 = low_price
fib_level_382 = low_price + (high_price - low_price) * 0.382
fib_level_50 = low_price + (high_price - low_price) * 0.5
fib_level_618 = low_price + (high_price - low_price) * 0.618
fib_level_786 = low_price + (high_price - low_price) * 0.786
fib_target = high_price + (high_price - low_price) * 0.27

// === DETECT SMA CROSS ===
ema1 = ta.sma(close, len1)
ema2 = ta.sma(close, len2)
buy_tr = ta.crossover(ema1, ema2)
sell_tr = ta.crossunder(ema1, ema2)

// === DETECT IMPULSE MOVE ===
// Added logic for 38.2% retracement level
impulse_detected_long_382 = close > fib_level_382 and close < fib_level_50 and buy_tr
impulse_detected_long_618 = close > fib_level_50 and close < fib_level_786 and buy_tr
impulse_detected_short_382 = close < fib_level_382 and close > fib_level_50 and sell_tr
impulse_detected_short_618 = close < fib_level_50 and close > fib_level_786 and sell_tr

// === POSITION SIZING ===
entry_price_long = fib_level_618
stop_loss_price_long = fib_level_0
entry_price_short = fib_level_618
stop_loss_price_short = high_price

take_profit_price_long = fib_target
take_profit_price_short = low_price - (high_price - low_price) * 0.27

position_size_long = risk_per_trade / math.abs(entry_price_long - stop_loss_price_long)
position_size_short = risk_per_trade / math.abs(entry_price_short - stop_loss_price_short)

// === TRACK DAILY LOSS ===
if daily_loss >= max_daily_risk
    strategy.close_all(comment="Max daily risk reached")

// === ENTRY AND EXIT CONDITIONS ===
// LONG Entry for 38.2% and 61.8% retracement levels
if impulse_detected_long_382 and daily_loss < max_daily_risk
    strategy.entry("Long_382", strategy.long, qty=position_size_long, comment="Long_382")
    strategy.exit("TakeProfit_382", "Long_382", limit=take_profit_price_long, stop=stop_loss_price_long)

if impulse_detected_long_618 and daily_loss < max_daily_risk
    strategy.entry("Long_618", strategy.long, qty=position_size_long, comment="Long_618")
    strategy.exit("TakeProfit_618", "Long_618", limit=take_profit_price_long, stop=stop_loss_price_long)

// SHORT Entry for 38.2% and 61.8% retracement levels
if impulse_detected_short_382 and daily_loss < max_daily_risk
    strategy.entry("Short_382", strategy.short, qty=position_size_short, comment="Short_382")
    strategy.exit("TakeProfit_382", "Short_382", limit=take_profit_price_short, stop=stop_loss_price_short)

if impulse_detected_short_618 and daily_loss < max_daily_risk
    strategy.entry("Short_618", strategy.short, qty=position_size_short, comment="Short_618")
    strategy.exit("TakeProfit_618", "Short_618", limit=take_profit_price_short, stop=stop_loss_price_short)

// === PLOT FIBONACCI LEVELS ===
plot(fib_level_0, color=color.red, title="Fib Level 0")
plot(fib_level_382, color=color.orange, title="Fib Level 38.2%")
plot(fib_level_50, color=color.yellow, title="Fib Level 50%")
plot(fib_level_618, color=color.green, title="Fib Level 61.8%")
plot(fib_level_786, color=color.blue, title="Fib Level 78.6%")
plot(fib_target, color=color.purple, title="Fib Target")
