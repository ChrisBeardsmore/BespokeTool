import streamlit as st
from app.utils.file_loader import load_supplier_data
from app.utils.formatter import preprocess_dataframe

def upload_file():
    return st.file_uploader("Upload Supplier Tender File", type=["xlsx"])

def get_user_inputs():
    sheet = st.selectbox("Select Pricing Type:", ['Standard', 'Green'])
    name = st.text_input("Company Name", "Example Co")
    reg = st.text_input("Company Reg", "12345678")
    return sheet, name, reg

def load_and_prepare(file, sheet):
    df = load_supplier_data(file, sheet)
    df = preprocess_dataframe(df)
    return df
