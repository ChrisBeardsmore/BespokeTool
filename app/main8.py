# Bespoke Tool – V7.py
# Builds on V6 with HH/NHH split, horizontal uplift UI, and TAC calculation

import streamlit as st
import pandas as pd
from io import BytesIO

# --- Streamlit Setup ---
st.set_page_config(layout="wide")
st.title("🔌 Bespoke Power Pricing Tool – V7 (HH/NHH Split + Uplift Input)")

# --- Upload Supplier Quote File ---
file = st.file_uploader("Upload Supplier Tender File (Excel)", type=["xlsx"])

if file:
    sheet = st.selectbox("Select Sheet", options=["Standard", "Green"])
    df_raw = pd.read_excel(file, sheet_name=sheet)

    # --- Detect HH ---
    def is_hh(row):
        return pd.notna(row.get("All Year - Day Rate (p/kWh)")) and \
               pd.notna(row.get("All Year - Night Rate (p/kWh)")) and \
               pd.notna(row.get("DUoS (p/KVA/Day)")) and \
               pd.notna(row.get("Standing Charge (p/day)"))

    df_raw["Is_HH"] = df_raw.apply(is_hh, axis=1)

    # --- Split HH and NHH ---
    df_nhh = df_raw[df_raw["Is_HH"] == False].copy()
    df_hh = df_raw[df_raw["Is_HH"] == True].copy()

    st.success(f"Loaded {len(df_nhh)} NHH rows and {len(df_hh)} HH rows.")

    # --- Function to Build Uplift Table ---
    def build_uplift_editor(df, meter_type):
        terms = [12, 24, 36]
        df['EAC'] = df['EAC'].fillna(0)
        base_cols = ["MPXN", "EAC", "Contract Length"]
        df['Contract Length'] = df['Contract Length'].astype(str)
        data = df[base_cols].drop_duplicates(subset=["MPXN", "Contract Length"]).pivot(index="MPXN", columns="Contract Length", values="EAC").reset_index()
        data.columns.name = None
        data = pd.merge(data, df[["MPXN", "EAC"]].drop_duplicates(), on="MPXN", how="left")

        for term in terms:
            suffix = f"{term}"
            term_str = f"{term}"
            sub_df = df[df['Contract Length'] == term_str]

            if meter_type == "NHH":
                cost_map = sub_df.set_index("MPXN")[[
                    "Standing Charge (p/day)",
                    "Day Rate (p/kWh)",
                    "Night Rate (p/kWh)",
                    "E/W Rate (p/kWh)"
                ]]
                for col in cost_map.columns:
                    data[f"{col} {term}m"] = data["MPXN"].map(cost_map[col])
                # Add uplift & TAC columns
                for col in ["SC", "Day", "Night", "E/W"]:
                    data[f"{col} Uplift {term}m"] = 0.000
                data[f"TAC {term}m (£)"] = 0.00

            else:  # HH
                cost_map = sub_df.set_index("MPXN")[[
                    "Standing Charge (p/day)",
                    "All Year - Day Rate (p/kWh)",
                    "All Year - Night Rate (p/kWh)",
                    "DUoS (p/KVA/Day)",
                    "Metering Charge (p/day)"
                ]]
                for col in cost_map.columns:
                    data[f"{col} {term}m"] = data["MPXN"].map(cost_map[col])
                for col in ["SC", "Day", "Night", "DUoS", "Metering"]:
                    data[f"{col} Uplift {term}m"] = 0.000
                data[f"TAC {term}m (£)"] = 0.00

        return data

    # --- Display NHH Table ---
    if not df_nhh.empty:
        st.subheader("📘 NHH Quotes – Uplift Entry")
        nhh_editor = build_uplift_editor(df_nhh, "NHH")
        edited_nhh = st.data_editor(nhh_editor, use_container_width=True, num_rows="dynamic")

    # --- Display HH Table ---
    if not df_hh.empty:
        st.subheader("📗 HH Quotes – Uplift Entry")
        hh_editor = build_uplift_editor(df_hh, "HH")
        edited_hh = st.data_editor(hh_editor, use_container_width=True, num_rows="dynamic")
