import streamlit as st

def logo(logopath: str,
         iconpath: str = None):
    # style helps ensure logo is large
    st.html("""
    <style>
        [alt=Logo] {
        height: 3rem;
        }
    </style>
    """)
    st.logo(logopath, 
            icon_image=iconpath, 
    )