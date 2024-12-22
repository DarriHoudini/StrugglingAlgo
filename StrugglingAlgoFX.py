import oandapyV20
import oandapyV20.endpoints.pricing as pricing
import oandapyV20.endpoints.orders as orders
import oandapyV20.types as types
from oandapyV20.types import StopLossDetails, TakeProfitDetails
from datetime import datetime, timedelta
import finnhub
import os
import logging
import time

# OANDA API credentials
OANDA_API_KEY = os.getenv('OANDA_API_KEY')  # Fetch from environment variables for security
OANDA_ACCOUNT_ID = os.getenv('OANDA_ACCOUNT_ID')
OANDA_API_URL = "https://api-fxpractice.oanda.com/v3"  # Use practice API for testing

# Finnhub API credentials
FINNHUB_API_KEY = os.getenv('FINNHUB_API_KEY')

# Initialize Finnhub client
finnhub_client = finnhub.Client(api_key=FINNHUB_API_KEY)

class OANDAForexBot:

    def __init__(self, account_id, api_key, instruments, cash_at_risk=0.5):
        self.client = oandapyV20.API(access_token=api_key)
        self.account_id = account_id
        self.instruments = instruments  # List of forex instruments like ["EUR_USD", "NZD_CAD", "AUD_USD"]
        self.cash_at_risk = cash_at_risk
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
                return float(price["bids"][0]["price"])
        return None

    def position_sizing(self, instrument):
        balance = self.get_account_balance()
        last_price = self.get_price(instrument)
        quantity = round((balance * self.cash_at_risk) / last_price, 2)  # Calculate trade size
        return balance, last_price, quantity

    def get_sentiment(self, instrument):
        # Get news sentiment for the instrument using Finnhub API
        today = datetime.now()
        three_days_prior = today - timedelta(days=3)
        news = finnhub_client.news sentiment({'category': 'forex', 'symbol': instrument})
        
        # Extract the sentiment data
        sentiment_scores = []
        for article in news:
            sentiment_scores.append(article['sentiment'])
        
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        return avg_sentiment

    def place_order(self, instrument, units, side, take_profit_price=None, stop_loss_price=None):
        # Create an OANDA market order with optional take-profit and stop-loss
        order = {
            "order": {
                "instrument": instrument,
                "units": str(units) if side == "buy" else str(-units),
                "type": "MARKET",
                "takeProfitOnFill": {"price": str(take_profit_price)} if take_profit_price else None,
                "stopLossOnFill": {"price": str(stop_loss_price)} if stop_loss_price else None,
            }
        }
        r = orders.OrderCreate(accountID=self.account_id, data=order)
        response = self.client.request(r)
        return response

    def run_strategy(self):
        for instrument in self.instruments:
            balance, last_price, quantity = self.position_sizing(instrument)
            sentiment = self.get_sentiment(instrument)

            # Check if the sentiment is strongly positive or negative and decide the action
            if sentiment > 0.5:  # Positive sentiment threshold
                if self.last_trade[instrument] == "sell":
                    self.place_order(instrument, quantity, "buy")  # Close short position
                self.place_order(
                    instrument,
                    quantity,
                    "buy",
                    take_profit_price=last_price * 1.20,
                    stop_loss_price=last_price * 0.95,
                )
                self.last_trade[instrument] = "buy"
            elif sentiment < -0.5:  # Negative sentiment threshold
                if self.last_trade[instrument] == "buy":
                    self.place_order(instrument, quantity, "sell")  # Close long position
                self.place_order(
                    instrument,
                    quantity,
                    "sell",
                    take_profit_price=last_price * 0.80,
                    stop_loss_price=last_price * 1.05,
                )
                self.last_trade[instrument] = "sell"

# Initialize and run the bot
if __name__ == "__main__":
    instruments = ["EUR_USD", "NZD_CAD", "AUD_USD", "USD_JPY", "EUR_JPY", "GBP_USD", "GBP_JPY"]  # Forex pairs to trade
    forex_bot = OANDAForexBot(
        account_id=OANDA_ACCOUNT_ID,
        api_key=OANDA_API_KEY,
        instruments=instruments,
        cash_at_risk=0.5,
    )

    # Logging setup
    logging.basicConfig(level=logging.INFO, filename='forex_bot.log')
    logging.info("Bot started")

    # Run the strategy and trade every 10 minutes
    while True:
        forex_bot.run_strategy()
        time.sleep(600)  # Sleep for 10 minutes before running again