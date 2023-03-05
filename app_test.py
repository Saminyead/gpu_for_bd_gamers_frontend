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
def get_best_card_df(budget:int = budget_input, which_query:str = "current"):
    """Gets which card is recommended, 1 price tier lower, or higher

    Args:
        budget (int, optional): The budget according which the recommended, 1 price tier lower, or 1 price tier higher is to be found. Defaults to budget_input.

        which_query (str, optional): 
        Defaults to "current".
        "current": for recommended gpu
        "lower": for 1 price tier lower
        "higher": for higher price tiers

    Returns:
        dataframe: Dataframe containing a single gpu according to our budget and which recommendation (recommendation, lower or higher)
    """
    which_query_dict = {
        "current" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget} ORDER BY {tier_score_col} DESC LIMIT 1",
        "lower" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price < {budget} ORDER BY {tier_score_col} DESC LIMIT 1",
        "higher" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price > {budget} ORDER BY {tier_score_col} ASC LIMIT 1",
    }
    query_price = which_query_dict[which_query]
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

# all recommended gpus
def get_best_cards_all(price:int):
    query_all_cards = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price = {price}"
    df_all_cards = pd.read_sql(sql=query_all_cards,con=conn)
    return df_all_cards


# function to execute upon budget_input
def upon_budget_input():
    get_best_card_df()
    if len(get_best_card_df()) == 0:
        too_low_gtx_1050_ti()
    else:
        st.write(f"Buy {get_best_card_df().gpu_unit_name[0]}")
        recommended_gpu_df_price = get_best_card_df().gpu_price[0]
        recommended_gpu_df = get_best_cards_all(recommended_gpu_df_price)
        recommended_gpu_tier_score = recommended_gpu_df.iloc[0][tier_score_col]
        st.write(recommended_gpu_df)

        df_1_lower = get_best_card_df(which_query="lower")
        price_per_tier_1_lower = df_1_lower.iloc[0][price_per_tier_score]
        tier_score_1_lower = df_1_lower.iloc[0][tier_score_col]
        tier_diff_1_lower = abs(tier_score_1_lower - recommended_gpu_tier_score)
        tier_diff_pct_1_lower = tier_diff_1_lower / recommended_gpu_tier_score * 100
        tier_diff_pct_1_lower = "{:.2f}".format(tier_diff_pct_1_lower)

        if tier_diff_pct_1_lower < 15 and price_per_tier_1_lower < recommended_gpu_tier_score:
            df_1_lower_price = df_1_lower.gpu_price[0]
            price_diff_1_lower = recommended_gpu_df_price - df_1_lower_price
            price_diff_1_lower_pct = price_diff_1_lower / recommended_gpu_df_price * 100
            price_diff_1_lower_pct = "{:.2f}".format(price_diff_1_lower_pct)
            st.write(f"Save BDT. {price_diff_1_lower:,} by getting the {df_1_lower.gpu_unit_name[0]}")
            df_1_lower_all = get_best_cards_all(price = df_1_lower_price)
            st.write(
                f"Provides within {tier_diff_1_lower} of the value of {recommended_gpu_df.gpu_unit_name[0]} while costing {price_diff_1_lower_pct}"
            )
            st.write(df_1_lower_all)



# testing out button
st.button(label="Recommend Me",on_click=upon_budget_input)

if budget_input:
    upon_budget_input()