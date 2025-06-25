import json
import streamlit as st

# Initialize session state variables
def initialize_session_state(json_path: json):
    """Initialize all session state variables with default values"""
    try:
        with open(json_path, 'r') as file:
            default_values = json.load(file)
    except FileNotFoundError:
        print("File not found")
    except json.JSONDecodeError:
        print("Invalid JSON format")
    
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value