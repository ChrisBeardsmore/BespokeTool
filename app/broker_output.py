import streamlit as st
import pandas as pd
from app.utils.cost_calc import calculate_annual_cost
from app.utils.formatter import convert_df

def handle_output(uplifted_df):
    st.subheader("💼 Broker Output")

    output_rows = []

    for _, row in uplifted_df.iterrows():
        base = {
            'Company Name': row['Company Name'],
            'Company Reg': row['Company Reg'],
            'MPXN': row['MPXN'],
            'Standard/Green': row['Standard/Green'],
            'Contract Start Date': row['CSD'],
            'EAC (kWh)': row['EAC']
        }

        for term in ['12', '24', '36']:
            sc_col = f'Standing Charge (p/day) {term}m'
            ur_col = f'Standard Rate (p/kWh) {term}m'

            sc = row.get(sc_col, 0) + row.get(f'S/C Uplift {term}m', 0)
            ur = row.get(ur_col, 0) + row.get(f'Unit Rate Uplift {term}m', 0)
            cost = calculate_annual_cost(sc, ur, row['EAC'])

            base.update({
                f'Standing Charge {term}m (p/day)': round(sc, 3),
                f'Unit Rate {term}m (p/kWh)': round(ur, 3),
                f'Annual Cost {term}m (£)': cost
            })

        output_rows.append(base)

    final_df = pd.DataFrame(output_rows)
    st.dataframe(final_df, use_container_width=True)

    excel_data = convert_df(final_df)
    st.download_button("Download Broker Output", data=excel_data,
        file_name="broker_output_dyce_prices.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
