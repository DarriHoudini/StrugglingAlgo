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


def run_strategy(self):
    for instrument in self.instruments:
        balance, last_price, quantity = self.position_sizing(instrument)

        impulse_detected, impulse_direction, fib_levels = self.detect_impulse_and_fibs(
            instrument
        )

        if impulse_detected:
            entry_price = (
                fib_levels["61.8"]
                if impulse_direction == "bullish"
                else fib_levels["78.6"]
            )
            stop_loss_price = (
                fib_levels["0.0"]
                if impulse_direction == "bullish"
                else fib_levels["low"]
            )
            target_price = (
                fib_levels["-0.27"]
                if impulse_direction == "bullish"
                else fib_levels["-0.27"]
            )

            risk_per_trade = (
                0.02 if impulse_direction == "bullish" else 0.03
            ) * self.starting_balance

            # Calculate position size based on risk
            position_size = round(
                risk_per_trade / abs(entry_price - stop_loss_price), 2
            )

            if entry_price <= last_price <= fib_levels["78.6"]:
                # Place order
                side = "buy" if impulse_direction == "bullish" else "sell"
                self.place_order(
                    instrument,
                    position_size,
                    side,
                    take_profit_price=target_price,
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
