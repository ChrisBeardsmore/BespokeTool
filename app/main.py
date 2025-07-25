import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from dateutil.relativedelta import relativedelta
from utils.versioning import get_current_version

st.set_page_config(layout="wide")
st.markdown(f"**App Version:** `{get_current_version()}`")


# --- Helper Functions ---
def load_supplier_data(uploaded_file, sheet_name):
    return pd.read_excel(uploaded_file, sheet_name=sheet_name)

def calculate_annual_cost(sc, unit_rate, eac):
    return round((sc * 365) + (unit_rate * eac), 2)

@st.cache_data
def convert_df(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    output.seek(0)
    return output

def calculate_months(start, end):
    return (end.year - start.year) * 12 + (end.month - start.month)

# --- Streamlit UI ---
st.title('Bespoke Power Pricing Tool – Broker Output Format')

uploaded_file = st.file_uploader("Upload Supplier Tender File (Excel)", type=["xlsx"])

if uploaded_file:
    sheet_option = st.selectbox("Select Pricing Type:", ('Standard', 'Green'))
    df_all = load_supplier_data(uploaded_file, sheet_name=sheet_option)

    company_name = st.text_input("Enter Company Name:", "Example Company")
    company_reg = st.text_input("Enter Company Registration Number:", "12345678")

    df_all['CSD'] = pd.to_datetime(df_all['CSD'], dayfirst=True)
    df_all['CED'] = pd.to_datetime(df_all['CED'], dayfirst=True)
    df_all['Contract Length'] = df_all.apply(lambda row: calculate_months(row['CSD'], row['CED']), axis=1)
    df_all = df_all[df_all['Contract Length'].isin([12, 24, 36])]
    df_all['Contract Length'] = df_all['Contract Length'].astype(str)

    if 'EAC' not in df_all.columns:
        st.error("Missing 'EAC' column in input file.")
        st.stop()

    # --- Pivoting the Key Fields ---
    cost_fields = ['Standing Charge (p/day)', 'Standard Rate (p/kWh)', 'EAC']
    df = df_all.groupby(['MPXN', 'Contract Length'])[cost_fields].first().reset_index()
    df_pivot = df.pivot(index='MPXN', columns='Contract Length', values=cost_fields)
    df_pivot.columns = [f"{col[0]} {col[1]}m" for col in df_pivot.columns]
    df_pivot.reset_index(inplace=True)

    meta = df_all.groupby('MPXN')[['CSD']].first().reset_index()
    full_df = pd.merge(meta, df_pivot, on='MPXN', how='left')

    full_df['Company Name'] = company_name
    full_df['Company Reg'] = company_reg
    full_df['Standard/Green'] = sheet_option

    for term in ['12', '24', '36']:
        full_df[f'S/C Uplift {term}m'] = 0.000
        full_df[f'Unit Rate Uplift {term}m'] = 0.000

    st.subheader("Enter Uplifts Per MPXN & Contract Length")
    editable_cols = ['MPXN', 'CSD', 'Company Name', 'Company Reg', 'Standard/Green']
    for term in ['12', '24', '36']:
        editable_cols += [
            f"Standing Charge (p/day) {term}m",
            f"Standard Rate (p/kWh) {term}m",
            f"EAC {term}m" if f"EAC {term}m" in full_df.columns else 'EAC',
            f"S/C Uplift {term}m",
            f"Unit Rate Uplift {term}m"
        ]

    input_editor = st.data_editor(
        full_df[editable_cols],
        use_container_width=True,
        hide_index=True,
        column_config={col: st.column_config.NumberColumn(step=0.001) for col in full_df.columns if 'Uplift' in col},
        num_rows="dynamic"
    )

    if st.button("Generate Broker Output"):
        output_rows = []

        for _, row in input_editor.iterrows():
            base = {
                'Company Name': row['Company Name'],
                'Company Reg': row['Company Reg'],
                'MPXN': row['MPXN'],
                'Standard/Green': row['Standard/Green'],
                'Contract Start Date': row['CSD']
            }

            for term in ['12', '24', '36']:
                sc_col = f'Standing Charge (p/day) {term}m'
                ur_col = f'Standard Rate (p/kWh) {term}m'
                eac_col = f"EAC {term}m" if f"EAC {term}m" in row else 'EAC'

                sc_uplift = row.get(f'S/C Uplift {term}m', 0)
                ur_uplift = row.get(f'Unit Rate Uplift {term}m', 0)

                try:
                    sc = row.get(sc_col, 0) + sc_uplift
                    ur = row.get(ur_col, 0) + ur_uplift
                    eac = row.get(eac_col, row['EAC'])
                except:
                    sc, ur, eac = 0, 0, 0

                total_cost = calculate_annual_cost(sc, ur, eac)

                base.update({
                    f'Standing Charge {term}m (p/day)': round(sc, 3),
                    f'Unit Rate {term}m (p/kWh)': round(ur, 3),
                    f'Annual Cost {term}m (£)': total_cost
                })

            output_rows.append(base)

        final_output = pd.DataFrame(output_rows)
        st.success("Broker Output Generated")
        st.dataframe(final_output, use_container_width=True)

        excel_data = convert_df(final_output)
        st.download_button(
            label="Download Broker Output",
            data=excel_data,
            file_name='broker_output_dyce_prices.xlsx',
            mime='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
