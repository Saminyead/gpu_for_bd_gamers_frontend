import streamlit as st
import pandas as pd
from app_functions import get_best_cards_all,recommend_col,init_connection

st.title("Get Any GPU Information Here")

# for use in other pages
if 'db_connection' not in st.session_state:
    st.session_state['db_connection'] = init_connection()

all_available_gpu = pd.read_sql(
    sql="SELECT DISTINCT gpu_unit_name FROM lowest_prices_tiered ORDER BY gpu_unit_name",
    con=st.session_state.db_connection
)

gpu_selected = st.selectbox(label="Select a Graphics Card",options=all_available_gpu)

# we want to utilize the recommend_col function for showing gpu info
info_col, = st.columns(1)

# get_best_cards_all just gives a dataframe of all cards with a given gpu_unit_name
gpu_selected_df = get_best_cards_all(gpu_unit=gpu_selected,db_conn=st.session_state.db_connection)

recommend_col(
    col=info_col,
    col_btn_id='info_col',
    gpu_df=gpu_selected_df,
    db_conn=st.session_state.db_connection,
    show_title=False,
)