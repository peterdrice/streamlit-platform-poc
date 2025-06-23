import streamlit as st
import pandas as pd
import numpy as np

st.title('Simple Stock Chart App')

st.write("This is another sample app in a different category to test the automated deployment platform.")

# Create some fake stock data
data = pd.DataFrame({
  'Date': pd.to_datetime(['2023-01-01', '2023-01-02', '2023-01-03', '2023-01-04', '2023-01-05']),
  'Price': [150.5, 152.3, 151.9, 154.1, 155.0]
}).set_index('Date')

st.line_chart(data)
