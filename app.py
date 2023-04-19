import streamlit as st
import psycopg2
import pandas as pd
import time

from app_functions import *


# for wide configuration, looks better this way
st.set_page_config(
    page_title="BD Gamers' GPU for Budget",
    layout="wide")


# Initialize connection.
conn = init_connection()

# for use in other pages
if 'db_connection' not in st.session_state:
    st.session_state['db_connection'] = conn


# title and short descriptio of the app
st.title(':Blue[Buy the Best Graphics Card for Your Budget]')
st.caption('For Bangladeshi Gamers. Based on Live Data of the Bangladeshi GPU Market')


# dropdown for determining which tier score
is_ray_tracing = st.radio(
"According to you, is Ray Tracing worth paying more for?",
["Yes","No"],
help=r"""
Let's say, GPU A and GPU B were both the same price, but GPU A's average performance was 5% higher.
On the other hand,GPU B had ray tracing capabilities. Which would you prefer to buy?   
If GPU A, then select 'Yes'.   
If GPU B, then select 'No'.
"""
)

if is_ray_tracing=="Yes":
    tier_score_col = 'net_tier_score'
    price_per_tier_score = 'price_per_net_tier'
    tier_score_ui = 'Net Tier Score'
else:
    weighted_recommendation = "Consider both positive and negative traits of GPU"
    raw_perf_recommendation = "Consider raw performance only"
    tier_score_selection = st.radio(
        label="How do you want the GPU performance values to be calculated?",
        options=[weighted_recommendation,raw_perf_recommendation]
    )
    if tier_score_selection==weighted_recommendation:
        tier_score_col = 'non_rt_net_score'
        price_per_tier_score = 'price_per_non_rt_tier'
        tier_score_ui = 'Non-RT Tier Score'
    else:
        tier_score_col = 'base_tier_score'
        price_per_tier_score = 'price_per_base_tier'
        tier_score_ui = 'Base Tier Score'

# selected tier score
st.write(f"#### Selected Performance Score: *[{tier_score_ui}](https://github.com/Saminyead/gpu_for_bd_gamers/blob/master/docs/tier_score_simplified.md 'Click to learn more about Tier Scores.')* ")

# input budget
budget_input = st.number_input(
    label = "Enter your budget here in BDT. (***Only enter numbers***)",
    min_value = 0,
    step = 1000
)



# if budget too low
def too_low_gtx_1050_ti():
    query_gtx_1050_ti = f"SELECT * FROM lowest_prices_tiered ORDER BY gpu_price ASC LIMIT 1"
    lowest_price_gpu_query_output = pd.read_sql(sql=query_gtx_1050_ti,con=conn)
    price_lowest_price_gpu = lowest_price_gpu_query_output.gpu_price[0]
    lowest_price_gpu_df = pd.read_sql(
        sql=f"SELECT * FROM lowest_prices_tiered WHERE gpu_price = {price_lowest_price_gpu}",
        con=conn
    )
    lowest_price_gpu = lowest_price_gpu_df.gpu_unit_name.iloc[0]
    return st.write(
        f"No good GPU's to recommend for this budget. Consider increasing your budget to BDT. {price_lowest_price_gpu:,} to get the {lowest_price_gpu}"
        ) # the price is written like this to show thousand separator



# function to execute upon budget_input
def upon_budget_input(
    tier_score_for_upon_budget_input:str = tier_score_col,
    price_per_tier_for_upon_budget_input:str = price_per_tier_score,
    recommend_col_func:callable = recommend_col
):
    recommended_best_card_df = get_best_card_df(
        budget=budget_input,
        tier_score_query=tier_score_col,
        price_per_tier_query=price_per_tier_score,
        db_conn=conn
        )
    if len(recommended_best_card_df) == 0:
        too_low_gtx_1050_ti()
    else:
        # writing recommended GPU
        recommended_gpu_unit_name = recommended_best_card_df.gpu_unit_name[0]
        recommended_gpu_df_price = recommended_best_card_df.gpu_price[0]
        recommended_gpu_df = get_best_cards_all(recommended_gpu_unit_name,db_conn=conn)
        recommended_gpu_tier_score = recommended_gpu_df.iloc[0][tier_score_for_upon_budget_input]
        recommended_gpu_price_per_tier = recommended_gpu_df.iloc[0][price_per_tier_for_upon_budget_input]

        # finding out GPU 1 price tier lower
        df_1_lower = get_best_card_df(
            budget=recommended_gpu_df_price,
            which_query="lower",
            tier_score_query=tier_score_col,
            price_per_tier_query=price_per_tier_score,
            db_conn=conn
            )
        # for the GTX 1050 Ti, df_1_lower becomes an empty dataframe
        if len(df_1_lower) != 0:
            df_1_lower_gpu_unit = df_1_lower.gpu_unit_name[0]
            price_per_tier_1_lower = df_1_lower.iloc[0][price_per_tier_for_upon_budget_input]
            tier_score_1_lower = df_1_lower.iloc[0][tier_score_for_upon_budget_input]
            tier_diff_1_lower = abs(tier_score_1_lower - recommended_gpu_tier_score)
            tier_diff_pct_1_lower = tier_diff_1_lower / recommended_gpu_tier_score * 100

        # finding out GPU 1 price tier higher
        df_1_higher = get_best_card_df(
            budget= budget_input,
            which_query="higher",
            tier_score_query=tier_score_col,
            price_per_tier_query=price_per_tier_score,
            db_conn=conn)
        # expecting something similar to the df_1_lower happening
        if len(df_1_higher) != 0:
            df_1_higher_gpu_unit = df_1_higher.gpu_unit_name[0]
            price_per_tier_1_higher = df_1_higher.iloc[0][price_per_tier_for_upon_budget_input]


        # column design
        col_recommended,col_1_lower,col_1_higher = st.columns([1.2,1,1],gap='large')

        
        recommend_col_func(
            col = col_recommended,
            title = "recommended",
            gpu_df = recommended_gpu_df,
            tier_score_for_recommend_col=tier_score_col, 
            col_btn_id='recommended',
            budget=budget_input,
            db_conn = conn)
        
        # for recommending better value GPU 1 price tier below
        if len(df_1_lower) != 0:
            if price_per_tier_1_lower < recommended_gpu_price_per_tier and tier_diff_pct_1_lower < 10:
                df_1_lower_all = get_best_cards_all(df_1_lower_gpu_unit,db_conn=conn)
                recommend_col_func(
                    col = col_1_lower,
                    title = "1_lower",
                    gpu_df=df_1_lower_all,
                    compare_df=recommended_gpu_df,
                    tier_score_for_recommend_col=tier_score_col,
                    budget=budget_input,
                    col_btn_id='1_lower',
                    db_conn = conn)
        

        # for recommending better value GPU 1 price tier higher
        if len(df_1_higher) != 0:
            if price_per_tier_1_higher < recommended_gpu_price_per_tier:
                df_1_higher_all = get_best_cards_all(df_1_higher_gpu_unit,db_conn=conn)
                recommend_col_func(
                    col = col_1_higher,
                    title = "1_higher",
                    gpu_df = df_1_higher_all,
                    compare_df = recommended_gpu_df,
                    tier_score_for_recommend_col=tier_score_col,
                    budget=budget_input,
                    col_btn_id='1_higher',
                    db_conn = conn
                )
        

# testing out button
recommend_btn = st.button(label="Recommend Me")

if budget_input or recommend_btn:
    with st.spinner("###### Generating....."):
        time.sleep(1)
        upon_budget_input()