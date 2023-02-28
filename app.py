import streamlit as st
import psycopg2
import pandas as pd

# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource

def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()


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
        
        tier_score_col = recommended_gpu['net_tier_score']
        tier_score_col_1_lower = recommended_gpu_1_lower['net_tier_score']

        price_per_tier_col = recommended_gpu['price_per_net_tier']
        price_per_tier_col_1_lower = recommended_gpu_1_lower['price_per_net_tier']
        # for better value-for-money GPU for lower price
        if price_per_tier_col_1_lower < price_per_tier_col:
            price_diff_1_lower = recommended_gpu['gpu_price'] - recommended_gpu_1_lower['gpu_price']
            st.write(f"Save {price_diff_1_lower} by buying:")
            st.write(recommended_gpu_1_lower)

            tier_diff_1_lower = tier_score_col_1_lower - tier_score_col
            tier_pct_diff_1_lower = abs(tier_diff_1_lower / tier_score_col * 100)
            tier_pct_diff_1_lower = "{:.2f}".format(tier_pct_diff_1_lower)
            price_pct_diff_1_lower = price_diff_1_lower / recommended_gpu['gpu_price'] * 100
            # to round to 2 decimal places
            price_pct_diff_1_lower = "{:.2f}".format(price_pct_diff_1_lower)
            st.write(
                f"Performs within {tier_pct_diff_1_lower}% of the {recommended_gpu['gpu_unit_name']} for {price_pct_diff_1_lower}% lower price")
        

        # for better value-for-money GPU within 15% above budget and 10% above the 15% higher mark
        # dataframe for the above GPU's
        budget_input_1_higher = 15/100 * budget_input # 10% above budget [1 price step above budget]
        budget_input_2_higher = 10/100 * budget_input_1_higher
        budget_query_higher = "SELECT * FROM lowest_price_tiered WHERE"