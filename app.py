import streamlit as st
import psycopg2
import pandas as pd

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource

def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()

# which tier_score to choose
is_ray_tracing = st.selectbox(
    "Are you willing to pay a premium for Ray Tracing?",
    ["Yes","No"]
)

if is_ray_tracing=="Yes":
    which_tier_score = 'net_tier_score'
else:
    weighted_recommendation = "Weighted recommendation according to positive and negative special traits along with raw performance"
    raw_perf_recommendation = "Only on raw performance. Ignore everything else"
    tier_score_selection = st.selectbox(
        label="Which kind of recommendation do you want?",
        options=[weighted_recommendation,raw_perf_recommendation]
    )
    if tier_score_selection==weighted_recommendation:
        which_tier_score = 'non_rt_tier_score'
    else:
        which_tier_score = 'base_tier_score'

# function for button
st.button("bruh")

# user input their budget
budget_input = st.number_input(
    label="Enter your budget in BDT here",
    min_value=0
)
budget_query = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price<={budget_input} ORDER BY net_tier_score DESC LIMIT 2"

recommended_gpus_under_budget = pd.read_sql(sql=budget_query,con=conn)

# show recommended GPU's only after entering budget
if budget_input:
    # in case of budget lower than the price of the GTX 1050 Ti
    if len(recommended_gpus_under_budget)==0:
        st.write("No GPU's for your budget")
    else:
        recommended_gpu = recommended_gpus_under_budget.iloc[0]
        recommended_gpu_1_lower = recommended_gpus_under_budget.iloc[1]
        st.write(recommended_gpu)
        st.write(type(recommended_gpu))

        def tier_price_diff(current_gpu,other_gpu):
            current_gpu_tier_score = current_gpu['net_tier_score']
            other_gpu_tier_score = other_gpu['net_tier_score']
            tier_diff = current_gpu_tier_score - other_gpu_tier_score
            tier_diff_pct = abs(tier_diff / current_gpu_tier_score * 100)
            # round to 2 decimal places
            tier_diff_pct = "{:.2f}".format(tier_diff_pct)

            current_gpu_price = current_gpu['gpu_price']
            other_gpu_price = other_gpu['gpu_price']
            price_diff = current_gpu_price - other_gpu_price
            price_diff_pct = abs(price_diff / current_gpu_price * 100)
            price_diff_pct = "{:.2f}".format(price_diff_pct)

            st.write(f"tier_diff = {tier_diff}")
            if tier_diff>0:
                return st.write(
                    f"Performs within {tier_diff_pct}% of the {current_gpu['gpu_unit_name']} for {price_diff_pct}% lower price"
                )
            
            else:
                return st.write(
                    f"Costs {price_diff} more\nOffers {tier_diff_pct}% better value for {price_diff_pct}% higher price"
                )

    
        price_per_tier_col = recommended_gpu['price_per_net_tier']
        price_per_tier_col_1_lower = recommended_gpu_1_lower['price_per_net_tier']
        # for better value-for-money GPU for lower price
        if price_per_tier_col_1_lower < price_per_tier_col:
            price_diff_1_lower = recommended_gpu['gpu_price'] - recommended_gpu_1_lower['gpu_price']
            st.write(f"Save {price_diff_1_lower} by buying:")
            st.write(recommended_gpu_1_lower)

            tier_price_diff(
                current_gpu=recommended_gpu,
                other_gpu=recommended_gpu_1_lower
            )        

        # for better value-for-money GPU within 15% above budget and 10% above the 15% higher mark
        budget_input_1_higher = 15/100 * budget_input # 10% above budget [1 price step above budget]
        budget_input_2_higher = 10/100 * budget_input_1_higher # 15% above the 10% higher budget [2 price step above budget]
        budget_query_higher = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget_input_2_higher} ORDER BY net_tier_score DESC LIMIT 2"
        # dataframe for the above GPU's
        recommended_gpus_2_higher = pd.read_sql(sql=budget_query_higher,con=conn)
        if len(recommended_gpus_2_higher)==0 or recommended_gpus_2_higher.iloc[1]['price_per_net_tier'] < recommended_gpu.iloc[0]['price_per_net_tier']:
            pass
