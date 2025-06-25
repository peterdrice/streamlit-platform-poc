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

def group_data_by_period(df, date_col, grouping_period, week_start_day=None):
    """
    Group data by specified time period with flexible options
    
    Args:
        df: DataFrame with datetime index or date column
        date_col: Name of the date column
        grouping_period: 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
        week_start_day: For weekly grouping, day to start week ('monday', 'tuesday', etc.)
    
    Returns:
        DataFrame grouped by the specified period
    """
    df_copy = df.copy()
    
    if grouping_period == 'daily':
        # Already daily, just ensure proper grouping
        df_copy['period'] = df_copy[date_col].dt.date
    elif grouping_period == 'weekly':
        # Manual calculation for more reliable week start handling
        day_mapping = {
            'monday': 0, 'tuesday': 1, 'wednesday': 2, 'thursday': 3,
            'friday': 4, 'saturday': 5, 'sunday': 6
        }
        
        target_weekday = day_mapping.get(week_start_day.lower(), 0)  # Default to Monday
        
        # Calculate the start of week for each date
        def get_week_start(date_val):
            # Get the weekday (0=Monday, 6=Sunday)
            current_weekday = date_val.weekday()
            
            # Calculate days to subtract to get to target weekday
            days_back = (current_weekday - target_weekday) % 7
            
            # Get the start of the week
            week_start = date_val - pd.Timedelta(days=days_back)
            return week_start.date()
        
        df_copy['period'] = df_copy[date_col].apply(get_week_start)
        
    elif grouping_period == 'monthly':
        # Group by month (start of month)
        df_copy['period'] = df_copy[date_col].dt.to_period('M').dt.start_time.dt.date
    elif grouping_period == 'quarterly':
        # Group by quarter (start of quarter)  
        df_copy['period'] = df_copy[date_col].dt.to_period('Q').dt.start_time.dt.date
    elif grouping_period == 'yearly':
        # Group by year (start of year)
        df_copy['period'] = df_copy[date_col].dt.to_period('Y').dt.start_time.dt.date
    
    return df_copy