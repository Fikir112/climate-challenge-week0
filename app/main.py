import streamlit as st
import pandas as pd
import plotly.express as px
import os

# --- Configuration ---
st.set_page_config(page_title="COP32 Climate Dashboard", layout="wide")

st.title(" African Climate Vulnerability Dashboard (COP32)")
st.markdown("Interactive analysis of Temperature and Precipitation (2015-2026)")

# --- Data Loading ---
@st.cache_data
def load_combined_data():
    # List the countries we have
    countries = ['ethiopia', 'kenya', 'tanzania', 'sudan', 'nigeria']
    all_dfs = []
    
    # We look for the data folder relative to where main.py is
    # '..' means go up one level, then into 'data'
    data_path = os.path.join(os.getcwd(), 'data') 
    
    for country in countries:
        file_path = os.path.join(data_path, f"{country}_clean.csv")
        if os.path.exists(file_path):
            temp_df = pd.read_csv(file_path)
            temp_df['Country'] = country.capitalize()
            all_dfs.append(temp_df)
    
    if not all_dfs:
        st.error("No cleaned CSV files found in the 'data' folder!")
        return pd.DataFrame()
        
    combined = pd.concat(all_dfs, ignore_index=True)
    combined['DATE'] = pd.to_datetime(combined['DATE'])
    return combined

df = load_combined_data()

if not df.empty:
    # --- Sidebar Widgets ---
    st.sidebar.header("Filters")
    
    # 1. Country Selector
    selected_countries = st.sidebar.multiselect(
        "Select Countries", 
        options=df['Country'].unique(), 
        default=df['Country'].unique()
    )
    
    # 2. Year Range Slider
    min_year, max_year = int(df['YEAR'].min()), int(df['YEAR'].max())
    year_range = st.sidebar.slider("Select Year Range", min_year, max_year, (min_year, max_year))
    
    # 3. Variable Selector
    variable = st.sidebar.selectbox("Select Climate Variable", ["T2M", "PRECTOTCORR", "RH2M", "WS2M"])

    # --- Filtering Logic ---
    filtered_df = df[
        (df['Country'].isin(selected_countries)) & 
        (df['YEAR'] >= year_range[0]) & 
        (df['YEAR'] <= year_range[1])
    ]

    # --- Dashboard Layout ---
    col1, col2 = st.columns(2)

    with col1:
        st.subheader(f"Timeline of {variable}")
        # Group by month for a cleaner line chart
        monthly_data = filtered_df.set_index('DATE').groupby(['Country', pd.Grouper(freq='ME')]).mean(numeric_only=True).reset_index()
        fig_line = px.line(monthly_data, x='DATE', y=variable, color='Country', markers=True)
        st.plotly_chart(fig_line, use_container_width=True)

    with col2:
        st.subheader(f"Distribution of {variable}")
        fig_box = px.box(filtered_df, x='Country', y=variable, color='Country')
        st.plotly_chart(fig_box, use_container_width=True)

    # Summary Section
    st.divider()
    st.subheader("Statistical Summary")
    st.dataframe(filtered_df.groupby('Country')[variable].describe().round(2), use_container_width=True)