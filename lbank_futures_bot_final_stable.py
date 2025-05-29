
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
        {"symbol": "BTCUSDT", "macd_cross": True},
        {"symbol": "ETHUSDT", "macd_cross": True},
        {"symbol": "OPUSDT", "macd_cross_down": True}
    ]

def generate_signature(params, secret):
    sorted_params = sorted(params.items())
    query = '&'.join([f"{k}={v}" for k, v in sorted_params])
    return hmac.new(secret.encode(), query.encode(), hashlib.sha256).hexdigest()

def get_current_price(symbol):
    symbol_formatted = symbol.replace("USDT", "_USDT")
    endpoint = f"/v2/ticker/24hr.do?symbol={symbol_formatted}"
    url = BASE_URL + endpoint
    try:
        response = requests.get(url)
        data = response.json()
        return float(data['ticker']['latest'])
    except Exception as e:
        print(f"❌ Error getting price: {e}")
        return None

def send_order_to_lbank(symbol, side):
    print(f"✅ {side.upper()} order placed: {symbol}")
    return get_current_price(symbol)

def monitor_position(symbol, entry_price, side):
    while True:
        current_price = get_current_price(symbol)
        if current_price is None:
            time.sleep(15)
            continue

        change_percent = ((current_price - entry_price) / entry_price) * 100
        if side == "buy":
            if change_percent >= TAKE_PROFIT_PERCENT:
                print(f"✅ TAKE PROFIT HIT on {symbol.upper()} at {current_price}")
                break
            elif change_percent <= -STOP_LOSS_PERCENT:
                print(f"❌ STOP LOSS HIT on {symbol.upper()} at {current_price}")
                break
        else:
            if -change_percent >= TAKE_PROFIT_PERCENT:
                print(f"✅ TAKE PROFIT HIT on {symbol.upper()} at {current_price}")
                break
            elif -change_percent <= -STOP_LOSS_PERCENT:
                print(f"❌ STOP LOSS HIT on {symbol.upper()} at {current_price}")
                break
        time.sleep(15)

def main():
    tokens = get_mock_data()
    for token in tokens:
        if token.get("macd_cross"):
            price = send_order_to_lbank(token["symbol"], "buy")
            if price:
                monitor_position(token["symbol"], price, "buy")
        elif token.get("macd_cross_down"):
            price = send_order_to_lbank(token["symbol"], "sell")
            if price:
                monitor_position(token["symbol"], price, "sell")
        time.sleep(SLEEP_SECONDS)

if __name__ == "__main__":
    main()
