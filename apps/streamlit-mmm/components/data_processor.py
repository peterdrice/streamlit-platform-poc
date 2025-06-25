import causalimpact
import streamlit as st
import pandas as pd

@st.cache_data(ttl=300)  # Cache for 5 minutes (300 seconds)
def fetch_kip_query(api_key: str, query_id: str) -> pd.DataFrame:
    """
    Fetch data from Kip Query with caching.
    
    Args:
        api_key: API key for authentication
        query_id: Query ID to fetch
        
    Returns:
        DataFrame with the query results
        
    Raises:
        Exception: If the request fails or returns invalid data
    """
    try:
        url = f"https://kip-query.keplergrp.com/api/queries/{query_id}/results.csv?api_key={api_key}"
        
        # Add some basic validation
        if not api_key or not query_id:
            raise ValueError("API key and Query ID are required")
            
        df = pd.read_csv(url)
        
        # Basic validation of the returned data
        if df.empty:
            raise ValueError("Query returned empty dataset")
            
        return df
        
    except Exception as e:
        st.error(f"Failed to fetch data from Kip Query: {str(e)}")
        st.stop()

@st.cache_data
def create_causal_impact_fit(
        pivot_df: pd.DataFrame,
        pre_period: tuple,
        post_period: tuple,
):
    impact = causalimpact.fit_causalimpact(
        data=pivot_df, pre_period=pre_period, post_period=post_period
    )

    return impact