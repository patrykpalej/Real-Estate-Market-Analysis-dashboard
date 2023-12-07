import os
import pandas as pd
import streamlit as st
import multiprocessing
import concurrent.futures
from dotenv import load_dotenv

from functions.lands import preprocess_lots
from functions.houses import preprocess_houses
from functions.apartments import preprocess_apartments


def generate_psql_connection_string(user, password, host, port, dbname):
    return f"postgresql://{user}:{password}@{host}:{port}/{dbname}"


def get_credentials():
    load_dotenv()
    user = os.environ["POSTGRESQL_USER"]
    password = os.environ["POSTGRESQL_PASSWORD"]
    host = os.environ["POSTGRESQL_HOST"]
    port = os.environ["POSTGRESQL_PORT"]
    dbname = os.environ["POSTGRESQL_DBNAME"]

    return user, password, host, port, dbname


def read_from_db(sql, conn_str):
    df = pd.read_sql(sql, conn_str)
    return df


def fetch_and_preprocess(property_type):

    pd.options.mode.chained_assignment = None

    preprocess_funcs_dict = {"lands": preprocess_lots, "houses": preprocess_houses,
                         "apartments": preprocess_apartments}

    sql_queries_dict = {"lands": "SELECT * FROM otodom_lands",
                    "houses": "SELECT * FROM otodom_houses",
                    "apartments": "SELECT * FROM otodom_apartments"}

    connection_string = generate_psql_connection_string(*get_credentials())
    preprocess_func = preprocess_funcs_dict[property_type]
    sql_query = sql_queries_dict[property_type]

    return (property_type,
            preprocess_func(read_from_db(sql_query, connection_string)))


def load_data_concurrently(threading):
    if threading:
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(fetch_and_preprocess, prop)
                       for prop in ["lands", "houses", "apartments"]]
            concurrent.futures.wait(futures)

            for future in futures:
                result = future.result()
                st.session_state.data[result[0]] = result[1]
    else:
        with multiprocessing.Pool() as pool:
            results_raw = pool.starmap(
                fetch_and_preprocess,
                [(prop,) for prop in ["lands", "houses", "apartments"]])

            for result in results_raw:
                st.session_state.data[result[0]] = result[1]
