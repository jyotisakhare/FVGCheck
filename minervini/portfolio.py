# portfolio.py
import math

class Portfolio:

    def __init__(self, capital, cfg):
        self.capital = capital
        self.positions = {}
        self.cfg = cfg

    def enter(self, symbol, price, date, index):

        allocation = self.capital/(self.cfg["MAX_POSITIONS"] - len(self.positions))

        # Inside your enter function...
        if math.isinf(allocation) or math.isnan(allocation):
            print(f"Error: Invalid allocation calculated: {allocation}")
            # Handle the error (e.g., set to 0, skip the trade, or raise a custom error)
            shares = 0
        else:
            shares = int(allocation) / price

        shares = int(shares)

        if allocation <= 0 or price <= 0:
            return

        if shares <= 0:
            return

        if self.capital <= allocation:
            return

        self.capital -= int(shares) * price

        self.positions[symbol] = {
            "entry": price,
            "shares": int(shares),
            "highest": price,
            "partial": False,
            "stop": price * 0.90,
            "entry_date": date,
            "entry_index": index + 1
        }
        print(f"symbol {symbol} - {date} -price -{price} - total {price*shares}")

    def update(self, symbol, row):

        pos = self.positions[symbol]

        pos["highest"] = max(pos["highest"], row["Close"])

        # Partial
        if not pos["partial"] and row["Close"] >= self.cfg["PARTIAL_PROFIT"] * pos["entry"]:
            sell = int(pos["shares"] * self.cfg["PARTIAL_SELL"])
            pos["shares"] -= sell
            self.capital += sell * row["Close"]
            pos["partial"] = True
            pos["stop"] = pos["entry"]
            print(f"partial booked {symbol}")

    def check_exit_ind(self, symbol, row, i, cfg, df):
        # print(f"checking exit india for {symbol}")
        pos = self.positions[symbol]

        # ===== DAYS HELD =====
        days_held = self.get_days_held(df, pos, i)

        # ===== 1. HARD STOP =====
        if row["Close"] < pos["stop"]:
            return True, "HARD STOP"

        # ===== HIGH-VOLUME SELLING EXIT AFTER PARTIAL =====
        if pos["partial"] and i >= 20:

            prev_close = df["Close"].iloc[i - 1]

            price_change = row["Close"] / prev_close - 1

            avg_vol_20 = df["Volume"].iloc[i - 20:i].mean()

            volume_ratio = (
                row["Volume"] / avg_vol_20
                if avg_vol_20 > 0
                else 0
            )

            if price_change <= -0.035 and volume_ratio >= 2.0:
                return True, "3.5% DROP + 2X AVG VOLUME AFTER PARTIAL"

        # ===== 2. INDIA LOGIC =====
        if days_held < 3:
            return False, None

        # if days_held > 30 and row["Close"] < pos["entry"]:
        #     return True, "LONG FAIL TRADE"

        # ===== 3. TRAILING STOP =====
        if pos["partial"]:
            if row["Close"] < cfg["TRAIL_AFTER_PARTIAL"] * pos["highest"]:
                return True, "TRAIL AFTER PARTIAL"
        else:
            if row["Close"] < cfg["TRAIL_INITIAL"] * pos["highest"]:
                return True, "TRAIL INITIAL"
            # elif row["Close"] > (pos["entry"]*1.20):
            #     return True, "Partial profit"

        # ===== 4. TREND EXIT =====
        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True, "TREND BREAK"

        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True, "TREND BREAK"

        if row["Close"] < row["EMA20"]:
            return False, "EMA20 touched"

        if row["Close"] < row["EMA10"]:
            return False, "EMA10 touched"

        return False, None

    def check_exit(self, symbol, row, i, cfg, df):

        if cfg["MARKET"] == "INDIA":
            return self.check_exit_ind(symbol, row, i, cfg, df)

        pos = self.positions[symbol]
        days_held = self.get_days_held(df, pos, i)

        # ===== HARD STOP =====
        if row["Close"] < pos["stop"]:
            return True, "HARD STOP"


        # ===== TRAILING =====
        if pos["partial"]:
            if row["Close"] < cfg["TRAIL_AFTER_PARTIAL"] * pos["highest"]:
                return True, "TRAIL AFTER PARTIAL"
        else:
            if row["Close"] < cfg["TRAIL_INITIAL"] * pos["highest"]:
                return True, "TRAIL INITIAL"

        # ===== TREND =====
        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True, "TREND BREAK"

        if row["Close"] < row["EMA20"]:
            return False, "EMA20 touched"

        if row["Close"] < row["EMA10"]:
            return False, "EMA10 touched"

        return False, None

    def get_days_held(self, df, pos, i):
        try:
            entry_idx = df.index.get_loc(pos["entry_date"])
            return i - entry_idx
        except:
            print(f"days held returned 0")
            return 0
