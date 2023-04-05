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
        "higher" : f"SELECT * FROM lowest_prices_tiered WHERE gpu_price > {budget} AND gpu_price < {budget_multiplier * budget} ORDER BY {price_per_tier_query} ASC LIMIT 1",
        "":""
    }
    query_price = which_query_dict[which_query]
    query_best_card_df = pd.read_sql(sql = query_price, con = db_conn)
    return query_best_card_df




def get_best_cards_all(gpu_unit:str,db_conn:psycopg2.extensions.connection):
    """get all cards from lowest_prices_tiered of the database according to a specific gpu_unit_name

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
    query_aib_cards = f"SELECT * FROM gpu_of_interest WHERE gpu_unit_name = '{gpu}' ORDER BY gpu_price ASC"
    df_all_aib_cards = pd.read_sql(sql=query_aib_cards,con=connection)
    return df_all_aib_cards