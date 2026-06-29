import json
import random

def patch_snapshot(path="app/data/snapshot.json"):
    with open(path, "r") as f:
        data = json.load(f)
        
    for ticker, series in data.items():
        if "open" in series:
            continue
            
        closes = series["close"]
        opens, highs, lows = [], [], []
        rng = random.Random(hash(ticker) & 0xFFFF)
        
        for c in closes:
            o = round(c * (1.0 + rng.gauss(0, 0.005)), 2)
            opens.append(o)
            highs.append(round(max(o, c) * (1.0 + abs(rng.gauss(0, 0.01))), 2))
            lows.append(round(min(o, c) * (1.0 - abs(rng.gauss(0, 0.01))), 2))
            
        series["open"] = opens
        series["high"] = highs
        series["low"] = lows
        
    with open(path, "w") as f:
        json.dump(data, f)
        
if __name__ == "__main__":
    patch_snapshot()
