import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

def display_uplift_grid(df, sheet_type, company, reg):
    df['Company Name'] = company
    df['Company Reg'] = reg
    df['Standard/Green'] = sheet_type

    for term in ['12', '24', '36']:
        df[f'S/C Uplift {term}m'] = 0.000
        df[f'Unit Rate Uplift {term}m'] = 0.000

    st.subheader("Enter Uplifts Per MPXN & Contract Length")
    gb = GridOptionsBuilder.from_dataframe(df)
    for term in ['12', '24', '36']:
        gb.configure_column(f'S/C Uplift {term}m', type=['numericColumn'], width=100)
        gb.configure_column(f'Unit Rate Uplift {term}m', type=['numericColumn'], width=150)

    grid_options = gb.build()
    grid = AgGrid(df, gridOptions=grid_options, editable=True, height=500)
    return grid['data']
