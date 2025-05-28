
import requests
import time
import hashlib
import hmac

# === CONFIG ===
API_KEY = "YOUR_API_KEY"
API_SECRET = "YOUR_SECRET_KEY"
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
        return float(data['ticker']['latest'])
    except:
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
        print(res.json())
        if entry_price:
            monitor_position(symbol, entry_price, side)
    except Exception as e:
        print(f"❌ Error placing {side} order: {e}")

def monitor_position(symbol, entry_price, side):
    if side == "buy":
        sl_price = entry_price * (1 - STOP_LOSS_PERCENT / 100)
        tp_price = entry_price * (1 + TAKE_PROFIT_PERCENT / 100)
    else:
        sl_price = entry_price * (1 + STOP_LOSS_PERCENT / 100)
        tp_price = entry_price * (1 - TAKE_PROFIT_PERCENT / 100)

    print(f"🔍 Monitoring {symbol.upper()} ({side.upper()})")
    print(f"🎯 SL: {sl_price:.5f}, TP: {tp_price:.5f}")

    while True:
        current_price = get_current_price(symbol)
        if not current_price:
            time.sleep(5)
            continue

        if (side == "buy" and current_price <= sl_price) or (side == "sell" and current_price >= sl_price):
            print(f"💀 STOP LOSS hit at {current_price:.5f}")
            break

        if (side == "buy" and current_price >= tp_price) or (side == "sell" and current_price <= tp_price):
            print(f"💸 TAKE PROFIT hit at {current_price:.5f}")
            reinvest_profit(symbol, side)
            break

        time.sleep(5)

def reinvest_profit(symbol, side):
    endpoint = "/v2/supplement/placeOrder"
    url = BASE_URL + endpoint
    reinvest_amount = ORDER_AMOUNT * (1 + TAKE_PROFIT_PERCENT / 100)

    reinvest_order = {
        "api_key": API_KEY,
        "symbol": symbol,
        "type": "market",
        "price": "0",
        "amount": str(round(reinvest_amount, 2)),
        "side": side,
        "timestamp": int(time.time() * 1000)
    }

    reinvest_order["sign"] = generate_signature(reinvest_order, API_SECRET)

    try:
        res = requests.post(url, data=reinvest_order)
        print(f"🔁 Reinvestment placed: {symbol.upper()} {side.upper()} for {reinvest_amount} USDT")
        print(res.json())
    except Exception as e:
        print(f"❌ Reinvestment error: {e}")

def run_screener():
    tokens = get_mock_data()
    for token in tokens:
        if token['volume'] > 1000000:
            # LONG condition
            if token.get('change', 0) >= 0.1 and token.get('rsi', 100) < 50 and token.get('macd_cross'):
                send_order_to_lbank(token['symbol'], "buy")

            # SHORT condition
            if token.get('change', 0) <= -0.1 and token.get('rsi', 0) > 70 and token.get('macd_cross_down'):
                send_order_to_lbank(token['symbol'], "sell")

if __name__ == "__main__":
    while True:
        run_screener()
        time.sleep(SLEEP_SECONDS)
