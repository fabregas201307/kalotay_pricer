import pandas as pd

def get_holidays_list(start_date: str, end_date: str) -> pd.DataFrame:
    prd = database.PRD() # database.PRD is placeholder for actual database connection
    query = f"SELECT * FROM holidays WHERE date >= '{start_date}' AND date <= '{end_date}'"
    holidays = prd.run_query(query)
    return holidays
