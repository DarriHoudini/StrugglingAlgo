import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
from oandapyV20.types import StopLossDetails, TakeProfitDetails
from datetime import datetime, timedelta

# OANDA API credentials
OANDA_API_KEY = "53aa1e1a3506aed9c9c12cd2febca8c5-07b9175931d4e54886100a3ef687b0f4"
OANDA_ACCOUNT_ID = "101-001-29240766-001"
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"  # Use practice API for testing

class OANDAForexBot:
    def __init__(self, account_id, api_key, instruments, starting_balance, max_daily_risk=0.15):
        self.client = oandapyV20.API(access_token=api_key)
        self.account_id = account_id
        self.instruments = instruments  # List of forex instruments like ["EUR_USD", "NZD_CAD", "AUD_USD"]
        self.starting_balance = starting_balance
        self.max_daily_risk = max_daily_risk * starting_balance
        self.daily_loss = 0
        self.last_trade = {instrument: None for instrument in self.instruments}

    def get_account_balance(self):
        # Get the account balance from OANDA
        account_url = f"{OANDA_API_URL}/accounts/{self.account_id}"
        response = self.client.request(oandapyV20.endpoints.AccountDetails(account_url))
        balance = float(response["account"]["balance"])
        return balance

    def get_price(self, instrument):
        # Get the latest price for the given instrument
        params = {"instruments": instrument}
        r = pricing.PricingInfo(accountID=self.account_id, params=params)
        response = self.client.request(r)
        prices = response["prices"]
        for price in prices:
            if price["instrument"] == instrument:
                return float(price["bids"][0]["price"]), float(price["asks"][0]["price"])
        return None, None

    def calculate_risk(self, risk_percentage, balance):
        return balance * risk_percentage

   def place_order(self, instrument, units, side, take_profit_price=None, stop_loss_price=None):
    # Create an OANDA market order with optional take-profit and stop-loss
    order = {
        "order": {
            "instrument": instrument,
            "units": str(units) if side == "buy" else str(-units),
            "type": "MARKET",
            "timeInForce": "FOK",  # Fill-or-Kill order type
        }
    }

    # Add take-profit and stop-loss if specified
    if take_profit_price:
        order["order"]["takeProfitOnFill"] = {"price": str(take_profit_price)}
    if stop_loss_price:
        order["order"]["stopLossOnFill"] = {"price": str(stop_loss_price)}

    # Submit the order
    r = orders.OrderCreate(accountID=self.account_id, data=order)
    response = self.client.request(r)
    return response

    def fibonacci_levels(self, high, low):
        # Calculate Fibonacci levels
        diff = high - low
        levels = {
            "0": low,
            "61.8": low + 0.618 * diff,
            "78.6": low + 0.786 * diff,
            "-27": high + 0.27 * diff,
        }
        return levels

    def run_strategy(self):
        for instrument in self.instruments:
            if self.daily_loss >= self.max_daily_risk:
                print(f"Daily risk limit reached. Stopping trades for {instrument}.")
                continue

            balance = self.get_account_balance()
            bid_price, ask_price = self.get_price(instrument)

            # Define impulse move (you need to implement logic to detect this)
            high = 1.1000  # Example value (replace with actual detection logic)
            low = 1.0900   # Example value (replace with actual detection logic)

            levels = self.fibonacci_levels(high, low)
            entry_price = None
            stop_loss_price = None
            take_profit_price = None

            if bid_price <= levels["78.6"]:
                # Bullish entry near 78.6% Fibonacci retracement
                entry_price = bid_price
                stop_loss_price = levels["0"]
                take_profit_price = levels["-27"]
                risk = self.calculate_risk(0.0002, self.starting_balance)  # 0.02% risk for buys

            elif ask_price >= levels["78.6"]:
                # Bearish entry near 78.6% Fibonacci retracement
                entry_price = ask_price
                stop_loss_price = levels["0"]
                take_profit_price = levels["-27"]
                risk = self.calculate_risk(0.0003, self.starting_balance)  # 0.03% risk for sells

            if entry_price and stop_loss_price and take_profit_price:
                # Calculate position size based on risk
                units = round(risk / abs(entry_price - stop_loss_price), 2)
                side = "buy" if bid_price <= levels["78.6"] else "sell"

                response = self.place_order(
                    instrument,
                    units,
                    side,
                    take_profit_price=take_profit_price,
                    stop_loss_price=stop_loss_price,
                )

                print(f"Placed {side} order for {instrument}: {response}")

                # Update daily loss if stop loss is hit
                self.daily_loss += risk

# Initialize and run the bot
if __name__ == "__main__":
    instruments = ["EUR_USD", "NZD_CAD", "AUD_USD", "USD_JPY", "EUR_JPY", "GBP_USD", "GBP_JPY"]  # Forex pairs to trade
    starting_balance = 100000  # Example starting balance

    forex_bot = OANDAForexBot(
        account_id=OANDA_ACCOUNT_ID,
        api_key=OANDA_API_KEY,
        instruments=instruments,
        starting_balance=starting_balance,
        max_daily_risk=0.15,  # 15% daily risk cap
    )

    forex_bot.run_strategy()
