
import requests
import time
import hmac
import hashlib

# === CONFIG ===
API_KEY = "your_api_key"
API_SECRET = "your_api_secret"
BASE_URL = "https://api.lbank.info"
LEVERAGE = 25
ORDER_AMOUNT_USDT = 50
STOP_LOSS_PERCENT = 5
TAKE_PROFIT_PERCENT = 20
SLEEP_SECONDS = 3600

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_current_price(symbol):
    endpoint = f"/v1/futures/openApi/symbolTicker?symbol={symbol}"
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['data']['lastPrice'])
    except Exception as e:
        print(f"❌ Error getting price: {e}")
        return None

def send_order_to_lbank(symbol, side):
    endpoint = "/v1/futures/openApi/placeOrder"
    url = BASE_URL + endpoint
    order = {
        "api_key": API_KEY,
        "symbol": symbol,
        "side": side.upper(),
        "type": "market",
        "size": ORDER_AMOUNT_USDT,
        "positionMode": "oneway",
        "open_type": "isolated",
        "leverage": LEVERAGE
    }
    try:
        response = requests.post(url, json=order)
        print("✅ Order response:", response.json())
    except Exception as e:
        print(f"❌ Error placing order: {e}")

def main():
    symbols = ["BTCUSDT", "ETHUSDT", "OPUSDT"]
    for symbol in symbols:
        price = get_current_price(symbol)
        if price is None:
            print(f"❌ Skipping {symbol} due to no price data.")
            continue
        send_order_to_lbank(symbol, "buy")
        time.sleep(15)

if __name__ == "__main__":
    main()
