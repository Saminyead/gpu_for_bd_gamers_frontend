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
    price_per_tier_score = 'price_per_net_tier'
else:
    weighted_recommendation = "Weighted recommendation according to positive and negative special traits along with raw performance"
    raw_perf_recommendation = "Only on raw performance. Ignore everything else"
    tier_score_selection = st.selectbox(
        label="Which kind of recommendation do you want?",
        options=[weighted_recommendation,raw_perf_recommendation]
    )
    if tier_score_selection==weighted_recommendation:
        which_tier_score = 'non_rt_net_score'
        price_per_tier_score = 'price_per_non_rt_tier'
    else:
        which_tier_score = 'base_tier_score'
        price_per_tier_score = 'price_per_base_tier'


# user input their budget
budget_input = st.number_input(
    label="Enter your budget in BDT here",
    min_value=0
)


def get_best_card_price(
    budget:int = budget_input,
    which_recommendation:str = "current",
    higher_pct:int = 0
    ):
    """Gets the price of the top performing card, card that is 1 price tier lower, or 1 price tier higher given the budget

    Args:
        budget (int, optional): The input budget, or the price of the recommended card. Defaults to budget_input.
        which_recommendation (str, optional): "current", "lower" or "higher". Defaults to "current".
        higher_pct (int, optional): _description_. Defaults to 0.

    Returns:
        _type_: _description_
    """
    pct_price_multiplier = (higher_pct + 100) / 100
    query_price = {
        "current" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget} ORDER BY {which_tier_score} DESC LIMIT 1",
        "lower" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price < {budget} ORDER BY {which_tier_score} DESC LIMIT 1",
        "higher" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price > {budget} AND gpu_price <= {pct_price_multiplier * budget} ORDER BY {which_tier_score} ASC LIMIT 1"
    }
    query_best_card = query_price[which_recommendation]
    df_best_card = pd.read_sql(sql=query_best_card,con=conn)
    price_best_card = df_best_card.gpu_price[0]
    return price_best_card

def get_best_cards_all(price:int):
    query_all_best_cards = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price = {price}"
    df_all_best_cards = pd.read_sql(sql=query_all_best_cards,con=conn)
    return df_all_best_cards

class GPU_diff:
    import pandas as pd
    import streamlit as st
    def __init__(self,current_gpu:pd.DataFrame,other_gpu:pd.DataFrame):
        self.current_gpu = current_gpu
        self.other_gpu = other_gpu
        self.current_gpu_unit_name = current_gpu.iloc[0]['gpu_unit_name']
        self.other_gpu_unit_name = other_gpu.iloc[0]['gpu_unit_name']
        self.current_gpu_price = current_gpu.iloc[0]['gpu_price']
        self.other_gpu_price = other_gpu.iloc[0]['gpu_price']
        self.current_gpu_tier_score = current_gpu.iloc[0][which_tier_score]
        self.other_gpu_tier_score = other_gpu.iloc[0][which_tier_score]
        self.current_gpu_price_per_tier = current_gpu.iloc[0][price_per_tier_score]
        self.other_gpu_price_per_tier = other_gpu.iloc[0][price_per_tier_score]
        self.tier_diff = self.current_gpu_tier_score - self.other_gpu_tier_score
        self.price_diff = self.current_gpu_price - self.other_gpu_price
    
    def recommend(self):
        tier_diff_pct = abs(self.tier_diff / self.current_gpu_tier_score * 100)
        tier_diff_pct = "{:.2f}".format(tier_diff_pct)
        price_diff_pct = abs(self.price_diff / self.current_gpu_price * 100)
        price_diff_pct = "{:.2f}".format(price_diff_pct)

        if self.tier_diff>0:
            return st.write(
                f"Performs within {tier_diff_pct}% of the {self.current_gpu} for {price_diff_pct}% lower price"
            )
    
        else:
            return st.write(
                f"For BDT. {self.price_diff} more, offers {tier_diff_pct}% better value for just {price_diff_pct}% higher price"
            ) 

def show_recommedation():
    recommended_gpu_price = get_best_card_price()
    recommended_gpu_df = get_best_cards_all(recommended_gpu_price)

    # in case of budget lower than the price of the GTX 1050 Ti
    if len(recommended_gpu_df)==0:
        st.write("No GPU's to recommend for your budget")
    
    price_1_lower = get_best_card_price(which_recommendation="lower")
    df_1_lower = get_best_cards_all(price=price_1_lower)

    st.write(recommended_gpu_df)

    recommended_1_lower_diff = GPU_diff(current_gpu = recommended_gpu_df, other_gpu= df_1_lower)

    # for better value GPU for less money
    if recommended_1_lower_diff.current_gpu_price_per_tier > recommended_1_lower_diff.other_gpu_price_per_tier:

        # if the tier difference is within 15%
        if recommended_1_lower_diff < 15/100 * recommended_1_lower_diff.current_gpu_tier_score:
            st.write(
                f"Save BDT. {recommended_1_lower_diff.price_diff} by buying the {recommended_1_lower_diff.current_gpu_unit_name}"
            )
            st.write(recommended_1_lower_diff.current_gpu)
            recommended_1_lower_diff.recommend()


# implementing button
recommendation_btn = st.button(label="Recommend GPU",on_click=show_recommedation)

if budget_input:
    show_recommedation()


### commented code starts from here
# # show recommended GPU's only after entering budget
# if budget_input:

    
#     else:
#         recommended_gpu = recommended_gpus_under_budget.iloc[0]
#         recommended_gpu_1_lower = recommended_gpus_under_budget.iloc[1]
#         st.write(recommended_gpu)
#         st.write(type(recommended_gpu))

#         def tier_price_diff(current_gpu,other_gpu):
#             current_gpu_tier_score = current_gpu['net_tier_score']
#             other_gpu_tier_score = other_gpu['net_tier_score']
#             tier_diff = current_gpu_tier_score - other_gpu_tier_score
#             tier_diff_pct = abs(tier_diff / current_gpu_tier_score * 100)
#             # round to 2 decimal places
#             tier_diff_pct = "{:.2f}".format(tier_diff_pct)

#             current_gpu_price = current_gpu['gpu_price']
#             other_gpu_price = other_gpu['gpu_price']
#             price_diff = current_gpu_price - other_gpu_price
#             price_diff_pct = abs(price_diff / current_gpu_price * 100)
#             price_diff_pct = "{:.2f}".format(price_diff_pct)

#             st.write(f"tier_diff = {tier_diff}")
#             if tier_diff>0:
#                 return st.write(
#                     f"Performs within {tier_diff_pct}% of the {current_gpu['gpu_unit_name']} for {price_diff_pct}% lower price"
#                 )
            
#             else:
#                 return st.write(
#                     f"Costs {price_diff} more\nOffers {tier_diff_pct}% better value for {price_diff_pct}% higher price"
#                 )

    
#         price_per_tier_col = recommended_gpu['price_per_net_tier']
#         price_per_tier_col_1_lower = recommended_gpu_1_lower['price_per_net_tier']
#         # for better value-for-money GPU for lower price
#         if price_per_tier_col_1_lower < price_per_tier_col:
#             price_diff_1_lower = recommended_gpu['gpu_price'] - recommended_gpu_1_lower['gpu_price']
#             st.write(f"Save {price_diff_1_lower} by buying:")
#             st.write(recommended_gpu_1_lower)

#             tier_price_diff(
#                 current_gpu=recommended_gpu,
#                 other_gpu=recommended_gpu_1_lower
#             )        

#         # for better value-for-money GPU within 15% above budget and 10% above the 15% higher mark
#         budget_input_1_higher = 15/100 * budget_input # 10% above budget [1 price step above budget]
#         budget_input_2_higher = 10/100 * budget_input_1_higher # 15% above the 10% higher budget [2 price step above budget]
#         budget_query_higher = f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget_input_2_higher} ORDER BY net_tier_score DESC LIMIT 2"
#         # dataframe for the above GPU's
#         recommended_gpus_2_higher = pd.read_sql(sql=budget_query_higher,con=conn)
#         if len(recommended_gpus_2_higher)==0 or recommended_gpus_2_higher.iloc[1]['price_per_net_tier'] < recommended_gpu.iloc[0]['price_per_net_tier']:
#             pass
