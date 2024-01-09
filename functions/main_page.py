import streamlit as st


def main_page():
    st.markdown("""
        <style>
        p {font-size: 1.2rem;}
        li {font-size: 1.2rem !important;}
        div[data-testid="stMarkdownContainer"] > p{
            font-size: 1.5rem !important;
        }
        div[data-testid="stMarkdownContainer"] > ul > li{
            font-size: 1.3rem !important;
        }
        
        </style>""", unsafe_allow_html=True)

    st.title("Real Estate Market Analysis")
    st.markdown("## Project description")

    left_column, _, right_column = st.columns([4, 1, 3])

    with left_column:
        st.markdown("""In this project, I developed a system designed for **collection and analysis** of real estate offers. Its primary goal is to **estimate the market value** of various properties, including houses, lands, and apartments.


It consists of four stages:

- data scraping
- data visualization
- machine learning model for price estimation
- model API (in progress)

All data is collected exclusively for educational purposes and is not utilized commercially. Personal data is not stored.
""")

    with right_column:
        with st.expander("Web scraping"):
            st.markdown("""Data used in this project is obtained from two sources: 
- [https://www.otodom.pl/](https://www.otodom.pl/) 
- [https://www.domiporta.pl/](https://www.domiporta.pl/)

For each of them, three property types are considered:
- houses
- lands
- apartments

Each combination of source-property type corresponds to a single scraping class and a database table. 
""")

        with st.expander("Data visualization"):
            st.markdown("On the left sidebar you can find links to tabs with visualization of the scraped data.")

        with st.expander("Model training"):
            st.markdown("""In the initial approach, machine learning models were trained only using **Otodom data** as this service provides more information about the properties. A dedicated **Random Forest Regressor** model was developed for each type of property, employing a scikit-learn `Pipeline`. Prior to the model training, a **feature engineering** process was undertaken to preprocess the data before modeling.

The preprocessing steps on the example of **houses data** includes the following:
- Transformation of the advert type (**agency or private**) into a boolean value
- Transformation of the market type (**primary or secondary**) into a boolean value
- Label encoding of the **weekday** and **season** corresponding to when the offer was posted
- Calculating time difference between the offer and an arbitrarily chosen timestamp (2023-01-01) to reflect **offer's position on a timeline**
- Label encoding of the house location (**country/suburban/city**)
- One hot encoding of **province** and **subregion** of the property""")

        with st.expander("Model API"):
            st.markdown("Work in progress")
