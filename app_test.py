import streamlit as st
import psycopg2
import pandas as pd

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource

def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# dropdown for determining which tier score
is_ray_tracing = st.selectbox(
"Are you willing to pay a premium for Ray Tracing?",
["Yes","No"]
)

if is_ray_tracing=="Yes":
    tier_score_col = 'net_tier_score'
    price_per_tier_score = 'price_per_net_tier'
else:
    weighted_recommendation = "Weighted recommendation according to positive and negative special traits along with raw performance"
    raw_perf_recommendation = "Only on raw performance. Ignore everything else"
    tier_score_selection = st.selectbox(
        label="Which kind of recommendation do you want?",
        options=[weighted_recommendation,raw_perf_recommendation]
    )
    if tier_score_selection==weighted_recommendation:
        tier_score_col = 'non_rt_net_score'
        price_per_tier_score = 'price_per_non_rt_tier'
    else:
        tier_score_col = 'base_tier_score'
        price_per_tier_score = 'price_per_base_tier'

# input budget
budget_input = st.number_input(
    label = "Enter your budget here",
    min_value = 0
)

# recommend a GPU
def get_best_card_df(budget:int = budget_input):
    query_price = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget} ORDER BY {tier_score_col} DESC LIMIT 1"
    query_best_card_df = pd.read_sql(sql = query_price, con = conn)
    return query_best_card_df

# if budget too low
def too_low_gtx_1050_ti():
    query_gtx_1050_ti = f"SELECT * FROM lowest_prices_tiered WHERE gpu_unit_name = 'Geforce GTX 1050 Ti'"
    df_gtx_1050_ti = pd.read_sql(sql=query_gtx_1050_ti,con=conn)
    price_gtx_1050_ti = df_gtx_1050_ti.gpu_price[0]
    return st.write(
        f"No good GPU's to recommend for this budget. Consider increasing your budget to BDT. {price_gtx_1050_ti:,} to get the GTX 1050 Ti"
        ) # the price is written like this to show thousand separator

# function to execute upon budget_input
def upon_budget_input():
    get_best_card_df()
    if len(get_best_card_df()) == 0:
        too_low_gtx_1050_ti()
    else:
        st.write(f"Buy {get_best_card_df().gpu_unit_name[0]}")

# testing out button
st.button(label="Recommend Me",on_click=upon_budget_input)

if budget_input:
    upon_budget_input()