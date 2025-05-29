
import requests
import time
import hmac
import hashlib

# === CONFIG ===
API_KEY = "80aa8fc8-07aa-4a60-b91f-731a300684cb"
API_SECRET = "D1E04C51A4CBAD1BAF41999FCEE0CB68"
BASE_URL = "https://api.lbkex.com"
LEVERAGE = 25
ORDER_AMOUNT_USDT = 50
STOP_LOSS_PERCENT = 5
TAKE_PROFIT_PERCENT = 20
SLEEP_SECONDS = 3600

def get_mock_data():
    return [
        {"symbol": "BTCUSDT_SWAP", "macd_cross": True},
        {"symbol": "ETHUSDT_SWAP", "macd_cross": True},
        {"symbol": "OPUSDT_SWAP", "macd_cross_down": True},
    ]

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_current_price(symbol):
    endpoint = f"/swap/market/quote?symbol={symbol}"
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        data = response.json()
        return float(data["data"]["latestPrice"])
    except Exception as e:
        print(f"❌ Error getting price: {e}")
        return None

def send_order_to_lbank(symbol, side):
    endpoint = "/swap/order/place"
    url = BASE_URL + endpoint
    price = get_current_price(symbol)
    if price is None:
        print(f"❌ Skipping {symbol} due to no price data.")
        return

    base_order = {
        "symbol": symbol,
        "side": side,
        "type": "market",
        "open_type": "isolated",
        "leverage": LEVERAGE,
        "custom_id": str(int(time.time())),
        "price": price,
        "amount": ORDER_AMOUNT_USDT / price,
        "api_key": API_KEY
    }

    sign = generate_signature(base_order, API_SECRET)
    base_order["sign"] = sign

    try:
        response = requests.post(url, data=base_order)
        result = response.json()
        if result.get("result") == "true":
            print(f"✅ {side.upper()} order placed: {symbol}")
        else:
            print(f"❌ Order failed: {result}")
    except Exception as e:
        print(f"❌ Error placing order: {e}")

def main():
    while True:
        tokens = get_mock_data()
        for token in tokens:
            if token.get("macd_cross"):
                send_order_to_lbank(token["symbol"], "buy")
            elif token.get("macd_cross_down"):
                send_order_to_lbank(token["symbol"], "sell")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
