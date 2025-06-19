import requests
import json
from datetime import datetime
import os
import time

DATA_DIR = "data"
os.makedirs(DATA_DIR, exist_ok=True)

def fetch_symbols():
    url = "https://fapi.binance.com/fapi/v1/ticker/24hr"
    data = requests.get(url, timeout=10).json()
    print("fetch_symbols data type:", type(data))
    if isinstance(data, dict) and "code" in data and "msg" in data:
        print(f"API Error {data['code']}: {data['msg']}")
        return []  # Hata varsa boş liste döndür
    return [item["symbol"] for item in data if item["symbol"].endswith("USDT")]

def fetch_prices():
    url = "https://fapi.binance.com/fapi/v1/ticker/price"
    data = requests.get(url, timeout=10).json()
    return {item["symbol"]: float(item["price"]) for item in data}

def fetch_agg(symbol):
    url = f"https://fapi.binance.com/fapi/v1/aggTrades?symbol={symbol}&limit=1000"
    data = requests.get(url, timeout=10).json()
    buy = sum(float(x["q"]) for x in data if not x["m"])
    sell = sum(float(x["q"]) for x in data if x["m"])
    return buy, sell

def take_snapshot():
    symbols = fetch_symbols()
    prices = fetch_prices()
    snapshot = []

    for i, symbol in enumerate(symbols):
        buy_vol, sell_vol = fetch_agg(symbol)
        price = prices.get(symbol, 0)
        snapshot.append({
            "symbol": symbol,
            "price": price,
            "buy_vol": buy_vol,
            "sell_vol": sell_vol
        })

        if (i + 1) % 100 == 0:
            time.sleep(10)

    now = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    filepath = os.path.join(DATA_DIR, f"snapshot_{now}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(snapshot, f, indent=2)
    print(f"Snapshot saved to {filepath}")

if __name__ == "__main__":
    take_snapshot()

