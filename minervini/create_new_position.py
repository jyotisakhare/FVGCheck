# app.py

import streamlit as st
import pandas as pd
import os

def trade_entry_widget():
    # Get all CSV files in current folder
    csv_files = ["minervini/positions.csv","minervini/positions_us.csv", "minervini/ravi_positions_ind.csv","minervini/ravi_positions_us.csv"]

    # If no CSV files exist, create default one
    if len(csv_files) == 0:
        default_file = "minervini/positions.csv"

        pd.DataFrame(columns=[
            "Symbol",
            "Entry Date",
            "Shares",
            "Entry Price",
            "Highest",
            "Partial",
            "Stop",
            "Entry Index",
            "Recom By"
        ]).to_csv(default_file, index=False)

        csv_files = [default_file]

    st.title("📈 Trade Entry App")

    # CSV selector
    selected_csv = st.selectbox(
        "📂 Select CSV File",
        csv_files
    )

    CSV_FILE = selected_csv

    # Create CSV file if not exists
    if not os.path.exists(CSV_FILE):
        df = pd.DataFrame(columns=[
            "Symbol",
            "Entry Date",
            "Shares",
            "Entry Price",
            "Highest",
            "Partial",
            "Stop",
            "Entry Index",
            "Recom By"
        ])
        df.to_csv(CSV_FILE, index=False)

    # Form
    with st.form("trade_form", width="stretch"):

        symbol = st.text_input("Symbol", value="BANDHANBNK.NS")

        entry_date = st.date_input("Entry Date")

        shares = st.number_input("Shares", min_value=1, step=1)

        entry_price = st.number_input(
            "Entry Price",
            min_value=0.0,
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
            "1% club"
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

        new_data = {
            "Symbol": symbol,
            "Entry Date": entry_date.strftime("%d/%m/%Y"),
            "Shares": shares,
            "Entry Price": entry_price,
            "Highest": default_highest,
            "Partial": False,
            "Stop": stop,
            "Entry Index": 0,
            "Recom By": recom_by
        }

        df = pd.read_csv(CSV_FILE)

        df = pd.concat([df, pd.DataFrame([new_data])], ignore_index=True)

        df.to_csv(CSV_FILE, index=False)

        st.success("✅ Trade saved successfully!")

    # Display existing trades
    st.subheader("📋 Saved Trades")

    df = pd.read_csv(CSV_FILE)

    st.dataframe(df, use_container_width=True)