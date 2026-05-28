# app.py

import streamlit as st

from sheetutils import connect_google_sheets, read_sheet

# =========================================================
# GOOGLE SHEETS CONFIG
# =========================================================
INDIA_SHEET = "positions"

US_SHEET = "positions_us"

# =========================================================
# GOOGLE SHEETS CONNECTION
# =========================================================

gs_client = connect_google_sheets()

# =========================================================
# APPEND ROW TO SHEET
# =========================================================
def append_trade(sheet_name, row_data):

    sheet = gs_client.open(sheet_name).sheet1

    sheet.append_row(row_data)

# =========================================================
# MAIN WIDGET
# =========================================================

def trade_entry_widget():

    # =========================================================
    # MARKET
    # =========================================================
    market = st.selectbox(
        "Market",
        ["US", "INDIA"],
        key="add_entry"
    )

    # =====================================================
    # SHEET SELECTION
    # =====================================================
    if market == "INDIA":
        SHEET_NAME = INDIA_SHEET
    else:
        SHEET_NAME = US_SHEET

    st.title("📈 Trade Entry App")

    # =====================================================
    # FORM
    # =====================================================

    # Form
    with st.form("trade_form"):

        symbol = st.text_input("Symbol", value="BANDHANBNK.NS")

        entry_date = st.date_input("Entry Date")

        shares = st.number_input("Shares", min_value=1, step=1)

        entry_price = st.number_input(
            "Entry Price",
            min_value=0.0,
            format="%.2f"
        )

        default_target = round(entry_price * 1.15, 2)

        target = st.number_input(
            "Target",
            min_value=0.0,
            value=default_target,
            format="%.2f"
        )

        # Default values based on entry price
        default_highest = entry_price
        default_stop = round(entry_price * 0.90, 2)

        stop = st.number_input(
            "Stop",
            min_value=0.0,
            value=default_stop,
            format="%.2f"
        )

        recommendation_options = [
            "minervini",
            "200 EMA",
            "Trade team",
            "twitter",
            "1% club",
            "custom"
        ]

        recom_by = st.selectbox(
            "Recommended By",
            recommendation_options
        )

        # Optional custom input
        if recom_by == "custom":
            recom_by = st.text_input("Enter Custom Recommendation Name")

        submitted = st.form_submit_button("Save Trade")

    # Save data
    if submitted:

        row_data = [
            symbol,
            entry_date.strftime("%d/%m/%Y"),
            shares,
            entry_price,
            default_highest,
            False,
            stop,
            0,
            recom_by,
            target
        ]

        append_trade(SHEET_NAME, row_data)

        st.success("✅ Trade saved successfully!")

        # =====================================================
        # DISPLAY SAVED TRADES
        # =====================================================
        st.subheader("📋 Saved Trades")

        try:

            df = read_sheet(
                SHEET_NAME,
                gs_client
            )

            if not df.empty:

                # fix arrow serialization issues
                for col in df.columns:
                    df[col] = df[col].astype(str)

                st.dataframe(
                    df,
                    width="stretch"
                )

            else:

                st.info("No trades found")

        except Exception as e:

            st.error(f"Error loading trades: {e}")

# =========================================================
# RUN APP
# =========================================================
st.set_page_config(
    page_title="Trade entry",
    page_icon=":memo:", # Can be an emoji, a path to an image, or a PIL Image object
    layout="wide",
)
st.title("🚀 Add Trade Entry")

trade_entry_widget()