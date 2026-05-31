# dashboard_pro.py

import streamlit as st
from collections import defaultdict
from symbol_loader import *
from strategy import *
from features import add_relative_strength
from config import CONFIG
from features import calculate_score

# ================= CONFIG =================
REFRESH_SECONDS = 3600

MARKETS = {
    "US": ["AAPL", "MSFT", "NVDA", "TSLA", "AMZN"],
    "INDIA": ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"]
}

INDEX_MAP = {
    "US": "^NDX",     # S&P 500
    "INDIA": "^NSEI"   # Nifty 50
}

# 1. Initialize the list in session_state if it doesn't exist
if "all_results" not in st.session_state:
    st.session_state.all_results = defaultdict(list)

# ================= DATA CLEANING =================
def clean_df(df):

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Open", "High", "Low", "Close", "Volume"]].copy()

    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    df.dropna(inplace=True)

    return df


# ================= INDICATORS =================
def add_indicators(df):

    df["EMA20"] = df["Close"].ewm(span=20).mean()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["SMA150"] = df["Close"].rolling(150).mean()

    df["52W_HIGH"] = df["Close"].rolling(252).max()
    df["VOL_AVG20"] = df["Volume"].rolling(20).mean()

    return df

# =========== fetch symbols candidates =========
def fetch_candidates(symbols) :
    row = 0
    local_candidates = []
    for symbol in symbols:

        df = fetch_stock(symbol)

        if df is None:
            continue

        df = add_relative_strength(df, index_df)

        i = len(df) - 1
        print(f"checking {symbol}")
        fail_reasons = check_entry(df, i, cfg, symbol, debug=True)
        if fail_reasons == "":
            score = calculate_score(df, i)
            local_candidates.append({
                "Symbol": symbol,
                "Score": score,
                "Price": float(df["Close"].iloc[-1]),
                "Volume": int(df["Volume"].iloc[-1]),
                "RS": round(df["RS"].iloc[-1], 3)
            })
        progress.progress((row + 1) / len(symbols))
        row = row + 1
    return local_candidates

# =========== check vsp contractions and return candidates =========
def fetch_vcp_candidates(symbols) :
    row = 0
    local_candidates = []
    for symbol in symbols:

        df = fetch_stock(symbol)

        if df is None:
            continue

        df = add_relative_strength(df, index_df)

        i = len(df) - 1
        print(f"checking {symbol}")
        if detect_vcp_breakout(df, debug=True):
            score = calculate_score(df, i)
            local_candidates.append({
                "Symbol": symbol,
                "Score": score,
                "Price": float(df["Close"].iloc[-1]),
                "Volume": int(df["Volume"].iloc[-1]),
                "RS": round(df["RS"].iloc[-1], 3)
            })
        progress.progress((row + 1) / len(symbols))
        row = row + 1
    return local_candidates

# =========== check 200 EMA cross candidates =========
def fetch_200_ema_candidates(symbols) :
    row = 0
    local_candidates = []
    for symbol in symbols:

        df = fetch_stock(symbol)

        if df is None:
            continue

        df = add_relative_strength(df, index_df)

        i = len(df) - 1
        print(f"checking {symbol}")
        if check_200ema_touch_and_near_high(df, i, debug=True):
            score = calculate_score(df, i)
            local_candidates.append({
                "Symbol": symbol,
                "Score": score,
                "Price": float(df["Close"].iloc[-1]),
                "Volume": int(df["Volume"].iloc[-1]),
                "RS": round(df["RS"].iloc[-1], 3)
            })
        progress.progress((row + 1) / len(symbols))
        row = row + 1
    return local_candidates

#=========== display candidates ========
def display_candidates(candidates, index_file):
    TOP_N = 10

    df_final = pd.DataFrame()

    if candidates:
        df_candidates = pd.DataFrame(candidates)
        df_candidates = df_candidates.sort_values(by="Score", ascending=False)
        df_final = df_candidates.head(TOP_N)

    # ===== DISPLAY =====
    if not df_final.empty:
        st.success(f"Top {TOP_N} Elite Setups {index_file}")
        st.dataframe(df_final, width='stretch')
    else:
        st.warning(f"No elite setups today {index_file}")


def display_all_results(final_result):
    for category, items in final_result.items():
        st.success(f"Category: {category} - {len(items)}")

        if items:
            df_candidates = pd.DataFrame(items)
            df_candidates = df_candidates.sort_values(by="Score", ascending=False)
            df_final = df_candidates
            # ===== DISPLAY =====
            if not df_final.empty:
                st.dataframe(df_final, width='stretch')


@st.cache_data(ttl=1500)
def fetch_stock(symbol):

    try:
        df = yf.download(symbol, period="2y", interval="1d", progress=False)

        if df.empty:
            return None

        df = clean_df(df)
        df = add_indicators(df)

        return df

    except:
        return None


# ================= FETCH INDEX =================
@st.cache_data(ttl=300)
def fetch_index(symbol):

    df = yf.download(symbol, period="1y", interval="1d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df[["Close"]].copy()
    df["EMA50"] = df["Close"].ewm(span=50).mean()
    df["EMA200"] = df["Close"].ewm(span=200).mean()

    df.dropna(inplace=True)

    return df


# ================= MARKET FILTER =================
def is_market_strong(index_df):

    if len(index_df) < 200:
        return False

    row = index_df.iloc[-1]

    if pd.isna(row["Close"]) or pd.isna(row["EMA50"]):
        return False

    return row["Close"] > row["EMA50"] > row["EMA200"]



# ================= UI =================
st.set_page_config(
    page_title="Screener",
    page_icon=":mag:", # Can be an emoji, a path to an image, or a PIL Image object
    layout="wide",
)
st.title("🚀 Momentum Scanner PRO")
progress = st.progress(0)

markets = load_market_symbols("")

selected_market = st.selectbox(
    "Select Market",
    list(markets.keys())
)

symbols = markets[selected_market]

if len(symbols) == 0:
    st.warning(f"No symbols found for {selected_market}")
    st.stop()

st.write(f"Loaded {len(symbols)} symbols from {selected_market}")

# ===== INDEX FILTER =====
index_symbol = INDEX_MAP[selected_market]
index_df = fetch_index(index_symbol)

market_ok = is_market_strong(index_df)

if market_ok:
    st.success(f"✅ Market is STRONG ({index_symbol})")
else:
    st.success(f"❌ Market is WEAK ({index_symbol}) — No trades allowed")
    # st.stop()

# ===== SCAN =====
cfg = CONFIG.copy()
cfg["MARKET"] = selected_market

if st.button("Load momentum Stocks"):
    candidates = fetch_candidates(symbols)
    st.session_state.all_results[selected_market+" Momentum minervini"] = candidates
    # display_candidates(candidates, "TOP Index")

if selected_market == "INDIA":
# ================= SINGLE STOCK CHECK =================
    st.markdown("---")
    st.subheader("🔍 Check Small and mid cap")
    if st.button("Check Small mid cap"):
        symbols = load_market_symbols_from_file("nifty_small_100.csv")
        candidates = fetch_candidates(symbols)
        st.session_state.all_results[selected_market + " Momentum minervini small cap"] = candidates
        # display_candidates(candidates, "small cap")
        symbols = load_market_symbols_from_file("nifty_mid_100.csv")
        candidates = fetch_candidates(symbols)
        st.session_state.all_results[selected_market + " Momentum minervini mid cap"] = (candidates)
        # display_candidates(candidates, "mid cap")
    if st.button("Check VCP contraction stocks"):
        symbols = load_market_symbols_from_file("nifty500.csv")
        candidates = fetch_vcp_candidates(symbols)
        # display_candidates(candidates, "VCP contraction stocks")
        st.session_state.all_results[selected_market + " VCP contraction"] = (candidates)

# ================= SINGLE STOCK CHECK =================
st.markdown("---")
st.subheader("🔍 Check Single Stock")

input_symbol = st.text_input("Enter Symbol (e.g. RELIANCE.NS or AAPL)")

if st.button("Check Entry"):

    if input_symbol.strip() == "":
        st.warning("Please enter a valid symbol")
    else:
        df = fetch_stock(input_symbol)

        if df is None:
            st.error("❌ Not enough data / invalid symbol")
        else:
            # add RS
            df = add_relative_strength(df, index_df)

            i = len(df) - 1

            fail_reasons = check_entry(df, i, cfg, input_symbol, debug=True)
            check_200_EMA = check_200ema_touch_and_near_high(df, i, debug=True)

            if fail_reasons == "" or check_200_EMA:
                score = calculate_score(df, i)

                st.success(f"✅ TRUE — Good to Enter ")
                st.success(f"minervini {fail_reasons}")
                st.success(f"200 EMA {check_200_EMA}")
                st.write({
                    "Symbol": input_symbol,
                    "Score": round(score, 2),
                    "Price": float(df["Close"].iloc[-1]),
                    "Volume": int(df["Volume"].iloc[-1]),
                    "RS": round(df["RS"].iloc[-1], 3)
                })

            else:
                st.error(f"❌ {fail_reasons}")

if st.button("Check 200 cross ema stocks"):
    candidates = fetch_200_ema_candidates(symbols)
    st.session_state.all_results[selected_market+" 200 CROSS EMA"] = candidates
    # display_candidates(candidates, "TOP 200 EMA cross stocks")

# Optional: Clear the list
if st.button("Clear List"):
    st.session_state.all_results = []
    st.rerun() # Refresh the UI immediately

display_all_results(final_result=st.session_state.all_results)

# ===== AUTO REFRESH =====
# st.caption(f"Auto refresh every {REFRESH_SECONDS}s")
# time.sleep(REFRESH_SECONDS)
# st.rerun()