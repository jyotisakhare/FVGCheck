# config.py

CONFIG = {
    "INITIAL_CAPITAL": 100000,
    "POSITION_SIZE": 0.10,
    "MAX_POSITIONS": 10,
    "TOP_N": 1,
    "MARKET":"US",

    # Filters
    "BREAKOUT_VOLUME_MULT": 1.2,
    "BREAKOUT_STRENGTH": 0.7,
    "MIN_ADX": 20,
    "MAX_EXTENSION": 1.15,
    "MIN_NEAR_HIGH": 0.85,
    "RS_LOOKBACK": 5,
    "MIN_LIQUIDITY": 5e6,
    "MIN_DAYS": 200,

    # Exit
    "PARTIAL_PROFIT": 1.10,
    "PARTIAL_SELL": 0.30,
    "TRAIL_INITIAL": 0.85,
    "TRAIL_AFTER_PARTIAL": 0.90,


}