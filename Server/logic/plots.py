# Server/logic/plots.py
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
from shared.config import PLOT_DIR
import warnings
warnings.filterwarnings("ignore", category=FutureWarning, module="pandas")

DATA_PATH = "Server/database/Arrest_Data_from_2020_to_Present.csv"

def preprocess_data():
    df = pd.read_csv(DATA_PATH)
    df['Arrest Date'] = pd.to_datetime(df['Arrest Date'], format='%m/%d/%Y %I:%M:%S %p', errors='coerce')
    df.dropna(subset=['Age', 'Sex Code', 'Descent Code', 'Arrest Date', 'Area ID', 'Charge Description'], inplace=True)
    df['Sex Code'] = df['Sex Code'].astype('category')
    df['Descent Code'] = df['Descent Code'].astype('category')
    df['Area ID'] = df['Area ID'].astype(str)
    df = df[(df['Age'] > 10) & (df['Age'] < 100)] 
    return df

def generate_plots():
    df = preprocess_data()
    plots_data = {}

    # Summary for dashboard
    plots_data['summary'] = {
        "total_arrests": int(len(df)),
        "unique_areas": int(df['Area ID'].nunique()),
        "date_range": f"{df['Arrest Date'].min().date()} - {df['Arrest Date'].max().date()}",
        "top_crime": df['Charge Description'].value_counts().idxmax(),
        "top_crime_count": int(df['Charge Description'].value_counts().max())
    }

    # Plot 1: Histogram of Age
    age_hist_data = df['Age'].value_counts(bins=10).sort_index()
    plots_data['age_hist'] = {
        "bins": [round(bin.mid, 1) for bin in age_hist_data.index],
        "counts": [int(count) for count in age_hist_data.values]
    }

    # Plot 2: Arrests over time (monthly)
    monthly = df['Arrest Date'].dt.to_period("M").value_counts().sort_index()
    plots_data['arrests_over_time'] = {
        "months": [str(month) for month in monthly.index],
        "counts": [int(count) for count in monthly.values]
    }

    # Plot 3: Arrests by Gender
    gender_counts = df['Sex Code'].value_counts()
    plots_data['gender_count'] = {
        "categories": [str(category) for category in gender_counts.index],
        "counts": [int(count) for count in gender_counts.values]
    }

    # Plot 4: Arrests by Area (Top 5)
    area_counts = df['Area ID'].value_counts().head(5)
    plots_data['area_count'] = {
        "areas": [str(area) for area in area_counts.index],
        "counts": [int(count) for count in area_counts.values]
    }

    # Plot 5: Top 5 Most Common Crimes
    crime_counts = df['Charge Description'].value_counts().head(5)
    plots_data['top_crimes'] = {
        "crimes": [str(crime) for crime in crime_counts.index],
        "counts": [int(count) for count in crime_counts.values]
    }

    return plots_data