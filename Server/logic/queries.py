import pandas as pd
from Server.logic.plots import preprocess_data

def get_arrests_by_time_period(time_period):
    df = preprocess_data()
    if time_period == "month":
        result = df['Arrest Date'].dt.to_period("M").value_counts().sort_index().to_dict()
    elif time_period == "week":
        result = df['Arrest Date'].dt.to_period("W").value_counts().sort_index().to_dict()
    else:
        raise ValueError("Invalid time period. Use 'month' or 'week'.")
    return {"time_period": time_period, "data": result}

def get_arrests_by_area(area_id):
    df = preprocess_data()
    result = df[df['Area ID'] == str(area_id)].shape[0]
    return {"area_id": area_id, "arrests": result}

def get_age_distribution():
    df = preprocess_data()
    age_distribution = df['Age'].value_counts(bins=10).sort_index()
    return {
        "bins": [round(bin.mid, 1) for bin in age_distribution.index],
        "counts": [int(count) for count in age_distribution.values]
    }

def get_most_common_crime(filter_value=None):
    df = preprocess_data()
    if filter_value:
        df = df[df['Charge Description'].str.contains(filter_value, case=False, na=False)]
    most_common = df['Charge Description'].value_counts().head(1)
    if most_common.empty:
        return {"error": "No crimes found for the given filter"}
    return {"crime": most_common.index[0], "count": int(most_common.values[0])}

