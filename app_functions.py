import streamlit as st
import pandas as pd
import psycopg2



def get_best_card_df(
    budget:int,
    tier_score_query:str,
    price_per_tier_query:str,
    db_conn:psycopg2.extensions.connection,
    budget_multiplier_pct:int = 20,
    which_query:str = "current"):
    """Gets which card is recommended, 1 price tier lower, or higher

    Args:
        budget (int, optional): The budget according which the recommended, 1 price tier lower, or 1 price tier higher is to be found. Defaults to 16500.
        tier_score_query (str): The tier_score according to which the query will be executed
        price_per_tier_query (str): The price_per_tier column
        db_conn (psycopg2.extensions.connection): The database connection
        budget_multiplier_pct (int, optional): Query will get GPU's whose price is this much percentage higher. Defaults to 20

        which_query (str, optional): 
        Defaults to "current".
        "current": for recommended gpu
        "lower": for 1 price tier lower
        "higher": for higher price tiers

    Returns:
        dataframe: Dataframe containing a single gpu according to our budget and which recommendation (recommendation, lower or higher)
    """
    budget_multiplier = (budget_multiplier_pct + 100) / 100
    which_query_dict = {
        "current" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price <= {budget} ORDER BY {tier_score_query} DESC LIMIT 1",
        "lower" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price < {budget} ORDER BY {tier_score_query} DESC LIMIT 1",
        "higher" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price > {budget} AND gpu_price < {budget_multiplier * budget} ORDER BY {price_per_tier_query} ASC LIMIT 1"
    }
    query_price = which_query_dict[which_query]
    query_best_card_df = pd.read_sql(sql = query_price, con = db_conn)
    return query_best_card_df




def get_best_cards_all(gpu_unit:str,db_conn:psycopg2.extensions.connection):
    """get all cards from lowest_prices_tiered table of the database according to a specific gpu_unit_name

    Args:
        gpu_unit (str): the gpu_unit_name according to which the query will be executed
        db_conn (psycopg2.extensions.connection): database connection

    Returns:
        pd.DataFrame: dataframe containing all GPU's with the gpu_unit_name
    """
    query_all_cards = f"SELECT * FROM lowest_prices_tiered WHERE gpu_unit_name = '{gpu_unit}'"
    df_all_cards = pd.read_sql(sql=query_all_cards,con=db_conn)
    return df_all_cards



def get_comment_table(connection:psycopg2.extensions.connection,query:str=f"SELECT * FROM comment_table"):
    """gets the comment_table from the database

    Args:
        connection (psycopg2.extensions.connection): database connection
        query (str, optional): the comment_table SELECT query. Defaults to f"SELECT * FROM comment_table".

    Returns:
        pd.DataFrame: dataframe containing the comment_table
    """
    return pd.read_sql(sql=query,con=connection)




def get_all_aib_cards_df(gpu:str,connection:psycopg2.extensions.connection):
    """gets all the cards of a particular gpu_unit_name

    Args:
        gpu (str): The gpu_unit_name according to which all GPU's will be fetched from the database
        connection (psycopg2.extensions.connection): database connection

    Returns:
        pd.DataFrame: DataFrame containing all AIB cards
    """
    # getting the latest date
    dates = pd.read_sql(
    sql="SELECT DISTINCT data_collection_date FROM gpu_of_interest",
    con=connection
    )
    dates_descending = dates.sort_values(by='data_collection_date',ascending=False)
    query_aib_cards = f"SELECT * FROM gpu_of_interest WHERE gpu_unit_name = '{gpu}' AND data_collection_date = '{dates_descending.data_collection_date.iloc[0]}' ORDER BY gpu_price ASC"
    df_all_aib_cards = pd.read_sql(sql=query_aib_cards,con=connection)
    return df_all_aib_cards




def recommend_col(
    col,
    col_btn_id:str,
    gpu_df:pd.DataFrame,
    db_conn:psycopg2.extensions.connection,
    budget:int = 16500, # as a generic budget
    tier_score_for_recommend_col:str = 'all',
    title:str = "recommended",
    show_title:bool = True,
    compare_df:pd.DataFrame = None
    ):
    """for displaying a st.column of either recommended gpu, 1 price tier lower, or 1 price tier higher

    Args:
        col (_type_): which column - col_recommended, col_1_lower or col_1_higher
        col_btn_id (str): "recommended", "1_lower" or "1_higher"
        title (str): "recommended","1_lower" or "1_higher"
        gpu_df (pd.DataFrame): which dataframe - recommended_df, df_1_lower_all or df_1_higher_all
        tier_score_for_recommend_col (str): imports tier_score_col into the scope of the function. Set it to "all" for All_GPU_Information
        compare_df (pd.DataFrame): for 1_lower and 1_higher, the dataframe to compare to (mainly juust recommended). Defailts to None
        budget (int): the input budget. Defaults to budget_input 
    """

    title_list = {
        "recommended":"Top Performing GPU for Your Budget",
        "1_lower":"Lower Price, Close in Performance",
        "1_higher":"Higher Price, Much Higher Performance",
        "":""
    }
    if show_title:
        col.header(title_list[title])
    else:
        col.empty()
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
    ##### :money_with_wings: Price of Lowest-price Model:   
    \u09F3 {gpu_df.gpu_price[0]:,}""")

    col.write(f"##### :chart_with_upwards_trend: Performance Score: ")  
    if tier_score_for_recommend_col == 'all':
        col.write(f"Base Tier Score: {gpu_df.iloc[0].base_tier_score:.2f}",unsafe_allow_html=True)
        col.write(f"Net Tier Score: {gpu_df.iloc[0].net_tier_score:.2f}",unsafe_allow_html=True)
        col.write(f"Non-RT Tier Score: {gpu_df.iloc[0].non_rt_net_score:.2f}",unsafe_allow_html=True)
    else:
        col.write(f"{gpu_df.iloc[0][tier_score_for_recommend_col]:.2f}")

    col.write("##### :shopping_trolley: Lowest-Price Models Available At:")
    for index, row in gpu_df.iterrows():
        col_retailer, col_gpu_name = col.columns(2)
        col_retailer.write(f"[{row.retailer_name}]({row.retail_url})")
        col_gpu_name.write(f"{row.gpu_name}")
    
    
    tier_score_query = f"SELECT gpu_unit_name,positive_comment_code,negative_comment_code FROM tier_score_table WHERE gpu_unit_name='{gpu_df.gpu_unit_name[0]}'"
    comment_code_gpu_df = pd.read_sql(sql=tier_score_query,con=db_conn)

    # for displaying the positive and negative traits/features of the GPU
    comment_table = get_comment_table(connection=db_conn)
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
    
    show_all_aib_cards_btn = col.checkbox(label='***Show More Models***',key=col_btn_id)
    if show_all_aib_cards_btn:
        col.write("##### Other Available Models:")
        for index,row in get_all_aib_cards_df(gpu_df.gpu_unit_name.iloc[0],db_conn).iterrows():
            col_gpu_name_aib,col_retailer_aib,col_aib_price = col.columns(3)
            col_gpu_name_aib.write(f"{row.gpu_name}")
            col_retailer_aib.write(f"[{row.retailer_name}]({row.retail_url})")
            col_aib_price.write(f"\u09F3 {row.gpu_price:,}")