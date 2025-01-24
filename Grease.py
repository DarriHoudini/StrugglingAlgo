//@version=5
strategy("Hedge Fund Swing Strategy (Trades Only)", overlay=true, pyramiding=1)

// === INPUT PARAMETERS ===
// Risk Management
fixed_account_balance = input.float(2000, title="Fixed Account Balance", group="Risk Management")
risk_per_trade_pct = input.float(2, title="Risk Per Trade (%)", group="Risk Management")
atr_length = input.int(14, title="ATR Length", group="Risk Management")
atr_multiplier = input.float(1.5, title="ATR Multiplier", group="Risk Management")

// Fibonacci Levels
fib_length = input.int(20, title="Fibonacci Lookback Period", group="Fibonacci Settings")

// Multi-Timeframe Analysis
use_htf_trend = input.bool(true, title="Use HTF Trend Filter", group="Trend Filter")
htf_trend_timeframe = input.string("1D", title="HTF Trend Timeframe", group="Trend Filter")
ema_length = input.int(200, title="EMA Length for Trend", group="Trend Filter")

// === MULTI-TIMEFRAME STRUCTURE ===
// HTF Trend
htf_close = request.security(syminfo.tickerid, htf_trend_timeframe, close)
htf_ema = request.security(syminfo.tickerid, htf_trend_timeframe, ta.ema(close, ema_length))
htf_trend = htf_close > htf_ema  // Bullish if price is above the 200 EMA

// Fibonacci Levels
fib_high = ta.highest(high, fib_length)
fib_low = ta.lowest(low, fib_length)
fib_range = fib_high - fib_low
fib_618 = fib_low + fib_range * 0.618
fib_50 = fib_low + fib_range * 0.5

// Liquidity Zones
liquidity_sweep_high = ta.highest(high, fib_length)  // Swing high for liquidity
liquidity_sweep_low = ta.lowest(low, fib_length)     // Swing low for liquidity

// === ATR CALCULATION ===
atr = ta.atr(atr_length)
stop_loss_distance = atr * atr_multiplier  // ATR-based stop-loss distance

// === POSITION SIZING ===
// Calculate position size to risk a fixed percentage of account balance
risk_per_trade = (risk_per_trade_pct / 100) * fixed_account_balance
position_size = risk_per_trade / stop_loss_distance

// === ENTRY CONDITIONS ===
// Long Condition: HTF bullish + price retraces to Fibonacci levels + above swing low
long_condition = htf_trend and close > fib_50 and close <= fib_618 and close > liquidity_sweep_low

// Short Condition: HTF bearish + price retraces to Fibonacci levels + below swing high
short_condition = not htf_trend and close < fib_50 and close >= fib_618 and close < liquidity_sweep_high

// === ENTRY AND EXIT LOGIC ===
// Long Trade Logic
long_stop_loss = liquidity_sweep_low - stop_loss_distance
long_take_profit = fib_high + (3 * atr)  // 3:1 reward-to-risk ratio
if long_condition and position_size > 0
    strategy.entry("Swing Long", strategy.long, qty=position_size)
    strategy.exit("Take Profit Long", from_entry="Swing Long", stop=long_stop_loss, limit=long_take_profit)
    label.new(bar_index, low, text="Long Entry", color=color.green, textcolor=color.white, size=size.small)

// Short Trade Logic
short_stop_loss = liquidity_sweep_high + stop_loss_distance
short_take_profit = fib_low - (3 * atr)  // 3:1 reward-to-risk ratio
if short_condition and position_size > 0
    strategy.entry("Swing Short", strategy.short, qty=position_size)
    strategy.exit("Take Profit Short", from_entry="Swing Short", stop=short_stop_loss, limit=short_take_profit)
    label.new(bar_index, high, text="Short Entry", color=color.red, textcolor=color.white, size=size.small)
