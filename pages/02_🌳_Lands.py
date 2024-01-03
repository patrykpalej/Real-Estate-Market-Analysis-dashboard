import streamlit as st
from datetime import date, timedelta

from functions.data_loading import load_data_concurrently
from functions.lands import plot_all, plot_by_month, plot_by_province, plot_map


st.set_page_config(layout="wide", page_title="Lands")

st.title("Lands")
st.header("Filters")

st.markdown(
        """
       <style>
        .stNumberInput {
            margin-bottom: 2em;

       </style>
   """, unsafe_allow_html=True)

try:
    df = st.session_state.data["lands"]
except (KeyError, AttributeError):
    with st.spinner(f'Data loading'):
        st.session_state.data = {}
        load_data_concurrently(True)
        df = st.session_state.data["lands"]

min_area, max_area, _, min_price, max_price, _, min_created, max_created = (
    st.columns([3, 3, 1, 3, 3, 1, 3, 3]))

province, _, location, _ = (
    st.columns([6, 1, 6, 7]))

with min_area:
    min_area_filter = min_area.number_input(
        "Minimum land area", min_value=df['land_area'].min(),
        value=df['land_area'].min(), max_value=df['land_area'].max())

with max_area:
    max_area_filter = max_area.number_input(
        "Maximum land area", min_value=df['land_area'].min(),
        value=df['land_area'].max(), max_value=df['land_area'].max())

with min_price:
    min_price_filter = min_price.number_input(
        "Minimum price", min_value=df['price'].min(), value=df['price'].min(),
        max_value=df['price'].max())

with max_price:
    max_price_filter = max_price.number_input(
        "Maximum price", min_value=df['price'].min(),
        value=df['price'].max(), max_value=df['price'].max())

with min_created:
    min_created_filter = min_created.date_input(
        "Offer added after", date.today() - timedelta(days=90))

with max_created:
    max_created_filter = max_created.date_input(
        "Offer added before", date.today())

with province:
    toggle_province = st.toggle('Filter provinces')
    if toggle_province:
        province_filter = province.multiselect(
            "Provinces", options=df["province"].unique(),
            default=df["province"].unique())

with location:
    location_filter = location.multiselect(
        "Location", options=df["location"].unique(),
        default=df["location"].unique())

df = df[(df["utc_created_at"].dt.date <= max_created_filter) &
        (df["utc_created_at"].dt.date >= min_created_filter) &
        (df["price"] >= min_price_filter) &
        (df["price"] <= max_price_filter) &
        (df["land_area"] <= max_area_filter) &
        (df["land_area"] >= min_area_filter) &
        (df["location"].isin(location_filter))]

if "province_filter" in locals():
    df = df[df["province"].isin(province_filter)]

st.markdown(f"Number of offers: {len(df)}")

st.header("Charts")

if len(df):
    with st.spinner(f'Processing {len(df)} offers'):
        fig_all = plot_all(df)
        st.plotly_chart(fig_all)
        st.markdown("***")        

    with st.spinner(f'Processing {len(df)} offers'):
        fig_by_month = plot_by_month(df)
        st.plotly_chart(fig_by_month)
        st.markdown("***")

    with st.spinner(f'Processing {len(df)} offers'):
        fig_by_province = plot_by_province(df)
        st.plotly_chart(fig_by_province)
        st.markdown("***")

    with st.spinner(f'Processing {len(df)} offers'):
        button_map = st.button('Show map')

        toggle_urls = st.toggle(
            'Show offers URLs (may take longer)')

        if button_map:
            fig_map = plot_map(df, urls=toggle_urls)
            if toggle_urls:
                st.markdown("Click on the point to see the URL")

            st.components.v1.html(fig_map._repr_html_(), width=1100,
                                  height=1200)
else:
    st.markdown("There are no offers that match your criteria")
