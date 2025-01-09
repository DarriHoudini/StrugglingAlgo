//@version=5
strategy("Delta Trend Following Strategy", overlay=true, pyramiding=1)

// === INPUT PARAMETERS ===
// Common Parameters
starting_balance = input.float(10000, title="Starting Balance", group="Common Settings")
risk_per_trade_pct = input.float(1, title="Risk Per Trade (%)", group="Risk Management")

// ATR Settings
atr_length = input.int(14, title="ATR Length", group="ATR Settings")
atr_multiplier = input.float(1.5, title="ATR Multiplier", group="ATR Settings")

// Moving Average Settings
ma_length = input.int(50, title="Moving Average Length", group="Trend Settings")

// Delta Settings
delta_lookback = input.int(10, title="Delta Lookback Period", group="Delta Settings")
delta_smoothing = input.int(3, title="Delta Smoothing", group="Delta Settings")

// === DYNAMIC ACCOUNT BALANCE ===
// Fetch current equity
current_equity = strategy.equity

// Calculate risk per trade (1% of current equity)
risk_per_trade = (risk_per_trade_pct / 100) * current_equity

// === ATR CALCULATION ===
atr = ta.atr(atr_length)
stop_loss_distance = atr * atr_multiplier  // ATR-based stop-loss distance

// === DELTA CALCULATION ===
// Simulated delta calculation: Difference between up volume and down volume
up_volume = math.sum(volume * (close > open ? 1 : 0), delta_lookback)
down_volume = math.sum(volume * (close < open ? 1 : 0), delta_lookback)
delta = ta.sma(up_volume - down_volume, delta_smoothing)  // Smoothed delta

// === POSITION SIZING ===
// Position size = risk per trade / stop-loss distance
position_size = risk_per_trade / stop_loss_distance

// === TREND LOGIC WITH DELTA ===
// Trend filter: Use a moving average and delta for confirmation
ma = ta.sma(close, ma_length)
long_condition = close > ma and delta > 0  // Price above MA and delta positive
short_condition = close < ma and delta < 0  // Price below MA and delta negative

// === ENTRY AND EXIT LOGIC ===
// Stop-loss and take-profit
long_stop_loss = close - stop_loss_distance
long_take_profit = close + (stop_loss_distance * 2)  // Risk-reward ratio of 2:1

short_stop_loss = close + stop_loss_distance
short_take_profit = close - (stop_loss_distance * 2)

// Execute long trade
if long_condition
    strategy.entry("Long", strategy.long, qty=position_size)
    strategy.exit("Long Exit", from_entry="Long", stop=long_stop_loss, limit=long_take_profit)

// Execute short trade
if short_condition
    strategy.entry("Short", strategy.short, qty=position_size)
    strategy.exit("Short Exit", from_entry="Short", stop=short_stop_loss, limit=short_take_profit)

// === DEBUGGING ===
label.new(bar_index, close, text="Delta: " + str.tostring(delta, "#.##") + "\nEquity: $" + str.tostring(current_equity, "#.##") + "\nPos Size: " + str.tostring(position_size, "#.####"), color=color.yellow)
