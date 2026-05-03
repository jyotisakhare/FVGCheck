# portfolio.py

class Portfolio:

    def __init__(self, capital, cfg):
        self.capital = capital
        self.positions = {}
        self.cfg = cfg

    def enter(self, symbol, price, date, index):

        allocation = self.capital * self.cfg["POSITION_SIZE"]
        shares = int(allocation / price)

        if shares <= 0:
            return

        self.capital -= shares * price

        self.positions[symbol] = {
            "entry": price,
            "shares": shares,
            "highest": price,
            "partial": False,
            "stop": price * 0.90,
            "entry_date": date,
            "entry_index": index + 1
        }

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

    def check_exit_ind(self, symbol, row, i, cfg, df):
        # print(f"checking exit india for {symbol}")
        pos = self.positions[symbol]

        # ===== DAYS HELD =====
        days_held = self.get_days_held(df, pos, i)

        # ===== 1. HARD STOP =====
        if row["Close"] < pos["stop"]:
            return True, "HARD STOP"

        # ===== 2. INDIA LOGIC =====
        if days_held < 3:
            return False, None

        if 3 <= days_held <= 5:
            if row["Close"] < 0.97 * pos["entry"]:
                return True, "FAILED BREAKOUT"

        # ===== 3. TRAILING STOP =====
        if pos["partial"]:
            if row["Close"] < cfg["TRAIL_AFTER_PARTIAL"] * pos["highest"]:
                return True, "TRAIL AFTER PARTIAL"
        else:
            if row["Close"] < cfg["TRAIL_INITIAL"] * pos["highest"]:
                return True, "TRAIL INITIAL"

        # ===== 4. TREND EXIT =====
        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True, "TREND BREAK"

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

        return False, None

    def get_days_held(self, df, pos, i):
        try:
            entry_idx = df.index.get_loc(pos["entry_date"])
            return i - entry_idx
        except:
            print(f"days held returned 0")
            return 0
