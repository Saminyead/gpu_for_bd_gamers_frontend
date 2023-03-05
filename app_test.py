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

tier_and_price_per_tier = (tier_score_col,price_per_tier_score)
st.write(tier_and_price_per_tier)