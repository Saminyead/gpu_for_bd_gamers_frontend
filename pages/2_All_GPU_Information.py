import streamlit as st
import pandas as pd
from app_functions import get_best_cards_all,recommend_col

st.title("Get Any GPU Information Here")

all_available_gpu = pd.read_sql(
    sql="SELECT DISTINCT gpu_unit_name FROM lowest_prices_tiered ORDER BY gpu_unit_name",
    con=st.session_state.db_connection
)

st.write(all_available_gpu)