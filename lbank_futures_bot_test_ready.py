
import requests
import time
import hmac
import hashlib

# === CONFIG ===
API_KEY = "80aa8fc8-07aa-4a60-b91f-731a300684cb"
API_SECRET = "D1E04C51A4CBAD1BAF41999FCEE0CB68"
BASE_URL = "https://api.lbank.info"
LEVERAGE = 25
ORDER_AMOUNT_USDT = 50
STOP_LOSS_PERCENT = 5
TAKE_PROFIT_PERCENT = 20
SLEEP_SECONDS = 3600

def get_mock_data():
    return [
        {"symbol": "PEPE_USDT", "macd_cross": True},
        {"symbol": "VVV_USDT", "macd_cross": True},
        {"symbol": "FAIL_USDT", "macd_cross_down": True}
    ]

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_current_price(symbol):
    endpoint = f"/v2/futures/market/detail?symbol={symbol}"
    url = BASE_URL + endpoint
    try:
        res = requests.get(url)
        data = res.json()
        return float(data['data']['latest'])
    except Exception as e:
        print(f"❌ Error getting price: {e}")
        return None

def send_order_to_lbank(symbol, side):
    endpoint = "/v2/futures/order/place"
    url = BASE_URL + endpoint
    price = get_current_price(symbol)
    if not price:
        print(f"❌ Skipping {symbol} due to no price data.")
        return

    amount = round(ORDER_AMOUNT_USDT / price, 4)
    base_order = {
        "api_key": API_KEY,
        "symbol": symbol,
        "size": amount,
        "price": 0,
        "type": "market",
        "side": side,
        "open_type": "isolated",
        "leverage": LEVERAGE,
        "position_id": 0,
        "timestamp": int(time.time() * 1000)
    }
    base_order["sign"] = generate_signature(base_order, API_SECRET)

    try:
        res = requests.post(url, data=base_order)
        print(f"✅ {side.upper()} order attempted: {symbol}")
        print("Response:", res.text)
    except Exception as e:
        print(f"❌ Error placing order for {symbol}: {e}")

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
