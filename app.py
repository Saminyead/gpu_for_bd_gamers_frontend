import streamlit as st
import psycopg2
import pandas as pd
import time


# for wide configuration, looks better this way
st.set_page_config(
    page_title="BD Gamers' GPU for Budget",
    layout="wide")


# Initialize connection.
# Uses st.cache_resource to only run once.
@st.cache_resource(ttl=3600)
def init_connection():
    return psycopg2.connect(**st.secrets["postgres"])

conn = init_connection()


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




# recommend a GPU
def get_best_card_df(
    budget:int = budget_input, 
    which_query:str = "current",
    tier_score_query:str = tier_score_col,
    price_per_tier_query:str = price_per_tier_score,
    budget_multiplier_pct:int = 15):
    """Gets which card is recommended, 1 price tier lower, or higher

    Args:
        budget (int, optional): The budget according which the recommended, 1 price tier lower, or 1 price tier higher is to be found. Defaults to budget_input.

        which_query (str, optional): 
        Defaults to "current".
        "current": for recommended gpu
        "lower": for 1 price tier lower
        "higher": for higher price tiers

        tier_score_query(str,optional): tier_score_col from the dropdowns. Because using global variables in functions are apparently bad. Defaults to tier_score_col
        price_per_tier_query(str,optional): price_per_tier_score from the dropdowns. Because using global variables in functions are apparently bad. Defaults to price_per_tier_score
        budget_multiplier_pct (int, optional): Query will get GPU's whose price is this much percentage higher. Defaults to 15

    Returns:
        dataframe: Dataframe containing a single gpu according to our budget and which recommendation (recommendation, lower or higher)
    """
    budget_multiplier = (budget_multiplier_pct + 100) / 100
    which_query_dict = {
        "current" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget} ORDER BY {tier_score_query} DESC LIMIT 1",
        "lower" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price < {budget} ORDER BY {tier_score_query} DESC LIMIT 1",
        "higher" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price > {budget} AND gpu_price < {budget_multiplier * budget} ORDER BY {price_per_tier_query} ASC LIMIT 1",
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
def get_best_cards_all(gpu_unit:str):
    query_all_cards = f"SELECT * FROM lowest_prices_tiered WHERE gpu_unit_name = '{gpu_unit}'"
    df_all_cards = pd.read_sql(sql=query_all_cards,con=conn)
    return df_all_cards




# comment_table will be necessary to display the positive and negative attributes of the GPU later
def get_comment_table(query=f"SELECT * FROM comment_table",connection=conn):
    return pd.read_sql(sql=query,con=connection)




def get_all_aib_cards_df(gpu:str,connection=conn):
    query_aib_cards = f"SELECT * FROM gpu_of_interest WHERE gpu_unit_name = '{gpu}' ORDER BY gpu_price ASC"
    df_all_aib_cards = pd.read_sql(sql=query_aib_cards,con=connection)
    return df_all_aib_cards




# function for showing the columns
def recommend_col(
    col,
    col_btn_id:str,
    title:str,
    gpu_df:pd.DataFrame,
    tier_score_for_recommend_col:str = tier_score_col,
    compare_df:pd.DataFrame = None,
    budget:int=budget_input,
    ):
    """for displaying a st.column of either recommended gpu, 1 price tier lower, or 1 price tier higher

    Args:
        col (_type_): which column - col_recommended, col_1_lower or col_1_higher
        col_btn_id (str): "recommended", "1_lower" or "1_higher"
        title (str): "recommended","1_lower" or "1_higher"
        gpu_df (pd.DataFrame): which dataframe - recommended_df, df_1_lower_all or df_1_higher_all
        tier_score_for_recommend_col (str): imports tier_score_col into the scope of the function, just keep it default. defaults to tier_score_col
        compare_df (pd.DataFrame): for 1_lower and 1_higher, the dataframe to compare to (mainly juust recommended). Defailts to None
        budget (int): the input budget. Defaults to budget_input 
    """

    title_list = {
        "recommended":"Top Performing GPU for Your Budget",
        "1_lower":"Lower Price, Close in Performance",
        "1_higher":"Higher Price, Much Higher Performance"
    }
    col.header(title_list[title])
    col.write(f"### {gpu_df.gpu_unit_name[0]}")
    if title != "recommended":
        price_diff = abs(gpu_df.gpu_price[0] - compare_df.gpu_price[0])
        price_diff_pct = price_diff / compare_df.gpu_price[0] * 100
        price_diff_budget = abs(gpu_df.gpu_price[0] - budget)
        price_diff_budget_pct = price_diff_budget / budget * 100
        tier_diff = gpu_df.iloc[0][tier_score_for_recommend_col] - compare_df.iloc[0][tier_score_for_recommend_col]
        tier_diff_pct = abs(tier_diff / compare_df.iloc[0][tier_score_for_recommend_col] * 100)

        if tier_diff < 0:
            col.write(f"*Save BDT. {price_diff:,}*")
            for _ in range(1):
                col.write("")
            col.write(f"""
            **Performs within {tier_diff_pct:.1f}%**  
            **Cheaper by {price_diff_pct:.1f}%**""")

        
        else:
            col.write(f"*For BDT. {price_diff_budget:,} ({round(price_diff_budget_pct)}%) higher than your budget:*")
            col.write(f""" 
                **{tier_diff_pct:.1f}% higher performance**  
                **{price_diff_pct:.1f}% higher price**"""
            )


    else:
        for _ in range(6):
            col.write("")
    col.write(f"""
    ##### Price of Lowest-price Model:   
    \u09F3 {gpu_df.gpu_price[0]:,}""")
    col.write(f"""
    ##### Performance Score:   
    {gpu_df.iloc[0][tier_score_col]:.2f}""")
    col.write("##### Available At:")
    for index, row in gpu_df.iterrows():
        col_retailer, col_gpu_name = col.columns(2)
        col_retailer.write(f"[{row.retailer_name}]({row.retail_url})")
        col_gpu_name.write(f"{row.gpu_name}")
    
    
    tier_score_query = f"SELECT gpu_unit_name,positive_comment_code,negative_comment_code FROM tier_score_table WHERE gpu_unit_name='{gpu_df.gpu_unit_name[0]}'"
    comment_code_gpu_df = pd.read_sql(sql=tier_score_query,con=conn)

    # for displaying the positive and negative traits/features of the GPU
    comment_table = get_comment_table()
    positive_codes = comment_code_gpu_df['positive_comment_code'].loc[comment_code_gpu_df.gpu_unit_name==gpu_df.gpu_unit_name[0]].iloc[0]
    if positive_codes:  # sometimes if there are positive_comment_code is empty, in which case it is None
        for code in positive_codes.split():
            desc = comment_table.loc[comment_table.comment_code==code]['comment_desc'].iloc[0]
            col.write(f":white_check_mark: {desc}")
    negative_codes = comment_code_gpu_df['negative_comment_code'].loc[comment_code_gpu_df.gpu_unit_name==gpu_df.gpu_unit_name[0]].iloc[0]
    if negative_codes:  # sometimes if there are negative_comment_code is empty, in which case it is None
        for n_code in negative_codes.split():
            n_desc = comment_table.loc[comment_table.comment_code==n_code]['comment_desc'].iloc[0]
            col.write(f":heavy_exclamation_mark: {n_desc}")
    
    show_all_aib_cards_btn = col.checkbox(label='*Show More Models*',key=col_btn_id)
    if show_all_aib_cards_btn:
        col.write("##### Other Available Models:")
        for index,row in get_all_aib_cards_df(gpu_df.gpu_unit_name.iloc[0]).iterrows():
            col_gpu_name_aib,col_retailer_aib,col_aib_price = col.columns(3)
            col_gpu_name_aib.write(f"{row.gpu_name}")
            col_retailer_aib.write(f"[{row.retailer_name}]({row.retail_url})")
            col_aib_price.write(f"\u09F3 {row.gpu_price:,}")




# function to execute upon budget_input
def upon_budget_input(
    tier_score_for_upon_budget_input:str = tier_score_col,
    price_per_tier_for_upon_budget_input:str = price_per_tier_score,
    recommend_col_func:callable = recommend_col
):
    get_best_card_df()
    if len(get_best_card_df()) == 0:
        too_low_gtx_1050_ti()
    else:
        # writing recommended GPU
        recommended_gpu_unit_name = get_best_card_df().gpu_unit_name[0]
        recommended_gpu_df_price = get_best_card_df().gpu_price[0]
        recommended_gpu_df = get_best_cards_all(recommended_gpu_unit_name)
        recommended_gpu_tier_score = recommended_gpu_df.iloc[0][tier_score_for_upon_budget_input]
        recommended_gpu_price_per_tier = recommended_gpu_df.iloc[0][price_per_tier_for_upon_budget_input]

        # finding out GPU 1 price tier lower
        df_1_lower = get_best_card_df(budget=recommended_gpu_df_price,which_query="lower")
        # for the GTX 1050 Ti, df_1_lower becomes an empty dataframe
        if len(df_1_lower) != 0:
            df_1_lower_gpu_unit = df_1_lower.gpu_unit_name[0]
            price_per_tier_1_lower = df_1_lower.iloc[0][price_per_tier_for_upon_budget_input]
            tier_score_1_lower = df_1_lower.iloc[0][tier_score_for_upon_budget_input]
            tier_diff_1_lower = abs(tier_score_1_lower - recommended_gpu_tier_score)
            tier_diff_pct_1_lower = tier_diff_1_lower / recommended_gpu_tier_score * 100

        # finding out GPU 1 price tier higher
        df_1_higher = get_best_card_df(budget= budget_input,which_query="higher",budget_multiplier_pct=20)
        # expecting something similar to the df_1_lower happening
        if len(df_1_higher) != 0:
            df_1_higher_gpu_unit = df_1_higher.gpu_unit_name[0]
            price_per_tier_1_higher = df_1_higher.iloc[0][price_per_tier_for_upon_budget_input]


        # column design
        col_recommended,col_1_lower,col_1_higher = st.columns([1.2,1,1],gap='large')

        
        recommend_col_func(col = col_recommended,title = "recommended",gpu_df = recommended_gpu_df, col_btn_id='recommended')
        
        # for recommending better value GPU 1 price tier below
        if len(df_1_lower) != 0:
            if price_per_tier_1_lower < recommended_gpu_price_per_tier and tier_diff_pct_1_lower < 10:
                df_1_lower_all = get_best_cards_all(df_1_lower_gpu_unit)
                recommend_col_func(col = col_1_lower,title = "1_lower",gpu_df=df_1_lower_all,compare_df=recommended_gpu_df,col_btn_id='1_lower')
        

        # for recommending better value GPU 1 price tier higher
        if len(df_1_higher) != 0:
            if price_per_tier_1_higher < recommended_gpu_price_per_tier:
                df_1_higher_all = get_best_cards_all(df_1_higher_gpu_unit)
                recommend_col_func(
                    col = col_1_higher,
                    title = "1_higher",
                    gpu_df = df_1_higher_all,
                    compare_df = recommended_gpu_df,
                    col_btn_id='1_higher'
                )
        

# testing out button
recommend_btn = st.button(label="Recommend Me")

if budget_input or recommend_btn:
    with st.spinner("###### Generating....."):
        time.sleep(1)
        upon_budget_input()