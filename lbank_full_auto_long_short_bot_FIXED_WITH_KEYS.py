import requests
import time
import hashlib
import hmac

# === CONFIG ===
API_KEY = "80aa8fc8-07aa-4a60-b91f-731a300684cb"
API_SECRET = "D1E04C51A4CBAD1BAF41999FCEE0CB68"
BASE_URL = "https://api.lbank.info"
LEVERAGE = 50
ORDER_AMOUNT = 10
STOP_LOSS_PERCENT = 1.5
TAKE_PROFIT_PERCENT = 20
SLEEP_SECONDS = 3600

def get_mock_data():
    return [
        {'symbol': 'pepe_usdt', 'volume': 10000000, 'change': 0.22, 'rsi': 40, 'macd_cross': True},
        {'symbol': 'vvv_usdt', 'volume': 5000000, 'change': 0.35, 'rsi': 38, 'macd_cross': True},
        {'symbol': 'fail_usdt', 'volume': 4000000, 'change': -0.25, 'rsi': 78, 'macd_cross_down': True}
    ]

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_current_price(symbol):
    endpoint = f"/v2/ticker/24hr.do?symbol={symbol}"
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        data = response.json()
        if "data" in data and data["data"]:
            ticker_info = data["data"][0]["ticker"]
            return float(ticker_info["latest"])
        else:
            print(f"❌ Invalid data for: {symbol}")
            return None
    except Exception as e:
        print(f"❌ Error getting price: {e}")
        return None

def send_order_to_lbank(symbol, side):
    endpoint = "/v2/supplement/placeOrder"
    url = BASE_URL + endpoint
    base_order = {
        "api_key": API_KEY,
        "symbol": symbol,
        "type": "market",
        "price": "0",
        "amount": str(ORDER_AMOUNT),
        "side": side,
        "timestamp": int(time.time() * 1000)
    }
    base_order["sign"] = generate_signature(base_order, API_SECRET)
    try:
        res = requests.post(url, data=base_order)
        print(f"✅ {side.upper()} order placed: {symbol.upper()}")
        entry_price = get_current_price(symbol)
        if entry_price:
            monitor_position(symbol, entry_price, side)
    except Exception as e:
        print(f"❌ Error placing {side} order: {e}")

def monitor_position(symbol, entry_price, side):
    while True:
        current_price = get_current_price(symbol)
        if not current_price:
            time.sleep(10)
            continue
        change_percent = ((current_price - entry_price) / entry_price) * 100 if side == "buy" else ((entry_price - current_price) / entry_price) * 100
        if change_percent >= TAKE_PROFIT_PERCENT:
            print(f"🎯 TAKE PROFIT HIT on {symbol.upper()} at {current_price} (+{change_percent:.2f}%)")
            break
        elif change_percent <= -STOP_LOSS_PERCENT:
            print(f"⚠️ STOP LOSS HIT on {symbol.upper()} at {current_price} ({change_percent:.2f}%)")
            break
        time.sleep(10)

def main():
    while True:
        data = get_mock_data()
        for item in data:
            symbol = item['symbol']
            if item.get('macd_cross'):
                send_order_to_lbank(symbol, 'buy')
            elif item.get('macd_cross_down'):
                send_order_to_lbank(symbol, 'sell')
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
