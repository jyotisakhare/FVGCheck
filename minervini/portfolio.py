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

    def check_exit_ind(self, symbol, row, i, cfg):

        pos = self.positions[symbol]
        days_held = i - pos["entry_index"] + 1

        # ===== 1. HARD STOP (ALWAYS FIRST) =====
        if row["Close"] < pos["stop"]:
            return True

        # ===== 2. INDIA-SPECIFIC LOGIC =====
        if cfg["MARKET"] == "INDIA":

            # ---- Phase 1: Noise zone (0–2 days) ----
            if days_held < 3:
                return False  # ignore noise completely

            # ---- Phase 2: Breakout confirmation (3–5 days) ----
            if 3 <= days_held <= 5:
                # allow small dip, not full failure
                if row["Close"] < 0.97 * pos["entry"]:
                    return True

            # ---- Phase 3: Post-confirmation ----
            # trailing logic continues below

        # ===== 3. TRAILING STOP =====
        if pos["partial"]:
            # tighter after partial
            if row["Close"] < cfg["TRAIL_AFTER_PARTIAL"] * pos["highest"]:
                return True
        else:
            # looser before partial
            if row["Close"] < cfg["TRAIL_INITIAL"] * pos["highest"]:
                return True

        # ===== 4. TREND EXIT =====
        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True

        return False

    def check_exit(self, symbol, row, i, cfg):
        if cfg["MARKET"] == "INDIA":
            return self.check_exit_ind(symbol, row, i, cfg)

        pos = self.positions[symbol]

        days_held = i - pos["entry_index"]



        # ===== 1. HARD STOP (highest priority) =====
        if row["Close"] < pos["stop"]:
            return True

        # ===== FAILED BREAKOUT EXIT =====
        if days_held <= 5 and row["Close"] < pos["entry"] and cfg["MARKET"] == "INDIA":
            return True

        # ===== 2. TRAILING STOP =====
        if pos["partial"]:
            # After partial → tighter trailing
            if row["Close"] < self.cfg["TRAIL_AFTER_PARTIAL"] * pos["highest"]:
                return True
        else:
            # Before partial → looser trailing OR disable
            if row["Close"] < self.cfg["TRAIL_INITIAL"] * pos["highest"]:
                return True

        # ===== 3. TREND EXIT (only after partial) =====
        if pos["partial"] and row["Close"] < row["EMA50"]:
            return True

        return False

