import streamlit as st
import pandas as pd

st.set_page_config(layout="wide")
st.title("CSV File Uploader and Viewer")

st.write("Upload a CSV file to see its contents displayed in a table below.")

uploaded_file = st.file_uploader("Choose a CSV file", type="csv")

if uploaded_file is not None:
    try:
        df = pd.read_csv(uploaded_file)
        st.success("File uploaded successfully!")
        st.header("Dataframe Contents")
        st.dataframe(df)
    except Exception as e:
        st.error(f"An error occurred: {e}")
