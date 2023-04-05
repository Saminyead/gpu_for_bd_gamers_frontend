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