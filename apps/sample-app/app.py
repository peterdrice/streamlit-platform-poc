import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(layout="wide")
st.title('Proof-of-Concept Streamlit App')

st.write("This app demonstrates the successful deployment of a containerized Streamlit application on AWS ECS Fargate.")

# Sample Data Visualization
st.header("Sample Data Visualization")
chart_data = pd.DataFrame(
    np.random.randn(20, 3),
    columns=['a', 'b', 'c'])

st.line_chart(chart_data)

st.success("If you can see this, the manual deployment was a success!")
