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
    df.dropna(subset=['Age', 'Sex Code', 'Descent Code', 'Arrest Date'], inplace=True)
    df['Sex Code'] = df['Sex Code'].astype('category')
    df['Descent Code'] = df['Descent Code'].astype('category')

    df = df[(df['Age'] > 10) & (df['Age'] < 100)] 

    return df

def generate_plots():
    df = preprocess_data()

    # Prepare data for each plot
    plots_data = {}

    # Plot 1: Histogram of Age
    age_hist_data = df['Age'].value_counts(bins=10).sort_index()  # Reduce bins for simplicity
    plots_data['age_hist'] = {
        "bins": [round(bin.mid, 1) for bin in age_hist_data.index],  # Midpoints of bins
        "counts": [int(count) for count in age_hist_data.values]  # Counts per bin
    }

    # Plot 2: Arrests over time (monthly)
    monthly = df['Arrest Date'].dt.to_period("M").value_counts().sort_index()
    plots_data['arrests_over_time'] = {
        "months": [str(month) for month in monthly.index],  # Months as strings
        "counts": [int(count) for count in monthly.values]  # Arrest counts per month
    }

    # Plot 3: Countplot by gender
    gender_counts = df['Sex Code'].value_counts()
    plots_data['gender_count'] = {
        "categories": [str(category) for category in gender_counts.index],  # Gender categories
        "counts": [int(count) for count in gender_counts.values]  # Counts per gender
    }

    # Plot 4: Boxplot of age per Descent Code
    descent_groups = df.groupby('Descent Code', observed=False)['Age'].apply(list)
    plots_data['age_box_descent'] = {
        "categories": [str(category) for category in descent_groups.index],  # Descent categories
        "summary": {  # Send summary statistics instead of raw data
            str(category): {
                "min": int(min(ages)),
                "max": int(max(ages)),
                "median": int(pd.Series(ages).median()),
                "q1": int(pd.Series(ages).quantile(0.25)),
                "q3": int(pd.Series(ages).quantile(0.75))
            }
            for category, ages in descent_groups.items()
        }
    }

    return plots_data

# def get_plot_images():
#     plots = ["age_hist.png", "arrests_over_time.png", "gender_count.png", "age_box_descent.png"]
#     paths = [os.path.join(PLOT_DIR, name) for name in plots]
#     return paths