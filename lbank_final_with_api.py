
import time
import requests
import hmac
import hashlib

# LBank API credentials
API_KEY = "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"
API_SECRET = "user_secret_placeholder"

SYMBOL = "pepe_usdt"
LEVERAGE = 25
TRADE_AMOUNT = 50  # USDT
STOP_LOSS_PERCENT = 0.05
API_URL = "https://api.lbank.info"

def get_timestamp():
    return str(int(time.time() * 1000))

def sign(params, secret):
    sorted_params = sorted(params.items())
    sign_str = "&".join(f"{k}={v}" for k, v in sorted_params)
    sign_str += f"&secret_key={secret}"
    return hashlib.md5(sign_str.encode()).hexdigest().upper()

def place_order(symbol, amount, leverage, direction):
    endpoint = "/v2/swap/order/place"
    timestamp = get_timestamp()
    params = {
        "api_key": API_KEY,
        "symbol": symbol,
        "direction": direction,
        "order_type": "market",
        "size": amount,
        "leverage": leverage,
        "timestamp": timestamp
    }
    params["sign"] = sign(params, API_SECRET)
    response = requests.post(API_URL + endpoint, data=params)
    print("Order Response:", response.text)
    return response.json()

def get_price(symbol):
    response = requests.get(f"{API_URL}/v1/ticker.do?symbol={symbol}")
    return float(response.json()['ticker']['latest'])

def monitor_position(entry_price):
    while True:
        time.sleep(10)
        current_price = get_price(SYMBOL)
        change = (current_price - entry_price) / entry_price

        if change <= -STOP_LOSS_PERCENT:
            print("Stop loss hit. Closing trade.")
            place_order(SYMBOL, TRADE_AMOUNT, LEVERAGE, "sell")
            break
        elif change >= STOP_LOSS_PERCENT:
            print("Take profit hit. Reinvesting profits.")
            place_order(SYMBOL, TRADE_AMOUNT, LEVERAGE, "buy")
            break

def main():
    print("Placing initial long order...")
    place_order(SYMBOL, TRADE_AMOUNT, LEVERAGE, "buy")
    entry_price = get_price(SYMBOL)
    monitor_position(entry_price)

if __name__ == "__main__":
    main()
