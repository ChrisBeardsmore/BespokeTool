# main3.py
# Version 29 – HH/NHH Split Input with Pivoted Broker Output

import pandas as pd
import streamlit as st
from io import BytesIO

# --- Streamlit Setup ---
st.set_page_config(page_title="Bespoke Power Pricing Tool", layout="wide")
st.title("🔌 Dyce Broker Pricing Tool – Power (v29)")

# --- File Upload ---
file = st.file_uploader("Upload Yu Energy Power Pricing File (.xlsx)", type=[".xlsx"])

if file:
    raw_df = pd.read_excel(file, sheet_name=None)
    sheet = list(raw_df.keys())[0]
    df = raw_df[sheet].copy()

    st.success(f"Loaded sheet: {sheet} ({df.shape[0]} rows)")

    # --- HH Detection ---
    def detect_hh(row):
        populated_cols = row[['Standing Charge (p/day)',
                              'DUoS (p/KVA/Day)',
                              'All Year - Day Rate (p/kWh)',
                              'All Year - Night Rate (p/kWh)']].notna().sum()
        return populated_cols == 4

    df['Is_HH'] = df.apply(detect_hh, axis=1)

    # --- Uplift Input Blocks ---
    st.header("⚙️ Uplift Settings")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("NHH Uplifts (p/kWh or p/day)")
        nhh_uplifts = {
            'Day': st.number_input("Day Uplift", value=0.100, format="%.3f"),
            'Night': st.number_input("Night Uplift", value=0.080, format="%.3f"),
            'Evening_Weekend': st.number_input("E&W Uplift", value=0.070, format="%.3f"),
            'Standing Charge': st.number_input("SC Uplift (NHH)", value=5.000, format="%.3f")
        }

    with col2:
        st.subheader("HH Uplifts (p/kWh or p/day)")
        hh_uplifts = {
            'Standard Rate': st.number_input("Standard Rate Uplift", value=0.090, format="%.3f"),
            'Standing Charge': st.number_input("SC Uplift (HH)", value=4.000, format="%.3f"),
            'Capacity Rate': st.number_input("Capacity Uplift", value=1.000, format="%.3f"),
            'Metering Charge': st.number_input("Metering Uplift", value=0.500, format="%.3f")
        }

    # --- Apply Uplifts ---
    def apply_uplifts(row):
        if row['Is_HH']:
            row['Adj_Standard_Rate'] = row['All Year - Day Rate (p/kWh)'] + hh_uplifts['Standard Rate']
            row['Adj_Standing_Charge'] = row['Standing Charge (p/day)'] + hh_uplifts['Standing Charge']
            row['Adj_Capacity_Rate'] = row['DUoS (p/KVA/Day)'] + hh_uplifts['Capacity Rate']
            row['Adj_Metering_Charge'] = row['Metering Charge (p/day)'] + hh_uplifts['Metering Charge']
        else:
            row['Adj_Day'] = row['Day Rate (p/kWh)'] + nhh_uplifts['Day']
            row['Adj_Night'] = row['Night Rate (p/kWh)'] + nhh_uplifts['Night']
            row['Adj_EW'] = row['Evening Weekend Rate (p/kWh)'] + nhh_uplifts['Evening_Weekend']
            row['Adj_Standing_Charge'] = row['Standing Charge (p/day)'] + nhh_uplifts['Standing Charge']
        return row

    df = df.apply(apply_uplifts, axis=1)

    # --- Placeholder for Pivoting & TAC Calculation ---
    st.warning("Pivoted broker-facing output with TAC logic not yet implemented. Coming next.")

    # --- Export Preview ---
    st.dataframe(df.head(20))
