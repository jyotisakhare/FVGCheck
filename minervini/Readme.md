# Exit Strategy Explanation

## 🇮🇳 INDIA Exit Strategy (More Strict Early Control)

- **Hard Stop (always active)**
  - Exit if price falls below your stop loss (~10% below entry)

- **First 3 days → No exit (cool-off period)**
  - Trade is given time to work
  - No early exits

- **Day 3 to 5 → Breakout validation**
  - Exit if price drops below 97% of entry
  - Helps catch failed breakouts early

- **Trailing Stop (protect profits)**
  - Before partial profit:
    - Exit if price < 85% of highest price
  - After partial profit:
    - Exit if price < 90% of highest price

- **Trend Exit (after partial profit only)**
  - Exit if price falls below EMA50


## 🇺🇸 US Exit Strategy (Simpler, Trend-Following)

- **Hard Stop (always active)**
  - Exit if price < stop loss

- **No early breakout failure logic**
  - No 3–5 day rule
  - Trades are given more time

- **Trailing Stop (main exit driver)**
  - Before partial profit:
    - Exit if price < 85% of highest price
  - After partial profit:
    - Exit if price < 90% of highest price

- **Trend Exit (after partial profit only)**
  - Exit if price falls below EMA50


## 🔑 Key Differences

- **India**
  - Has early failure detection (3–5 day rule)
  - More defensive

- **US**
  - No early exit rules
  - More trend-following


## 🧠 Intuition

- India market = more volatile → stricter exits
- US market = smoother trends → flexible exits
