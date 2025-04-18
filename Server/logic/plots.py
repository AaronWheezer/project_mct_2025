# Server/logic/plots.py
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns
import os
from shared.config import PLOT_DIR

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
    if not os.path.exists(PLOT_DIR):
        os.makedirs(PLOT_DIR)

    df = preprocess_data()


    plt.figure(figsize=(8, 6))
    sns.histplot(df['Age'], bins=30, kde=True)
    plt.title("Histogram of Age")
    plt.savefig(f"{PLOT_DIR}/age_hist.png")
    plt.close()

    # Plot 2: Arrests over time (monthly)
    monthly = df['Arrest Date'].dt.to_period("M").value_counts().sort_index()
    plt.figure(figsize=(12, 6))
    monthly.plot(kind="line")
    plt.title("Arrests Over Time (Monthly)")
    plt.xlabel("Month")
    plt.ylabel("Number of Arrests")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(f"{PLOT_DIR}/arrests_over_time.png")
    plt.close()

    # Plot 3: Countplot by gender
    plt.figure(figsize=(6, 6))
    sns.countplot(x='Sex Code', data=df)
    plt.title("Arrests by Gender")
    plt.savefig(f"{PLOT_DIR}/gender_count.png")
    plt.close()

    # Plot 4: Boxplot of age per Descent Code
    plt.figure(figsize=(10, 6))
    sns.boxplot(x='Descent Code', y='Age', data=df)
    plt.title("Boxplot of Age by Descent Code")
    plt.savefig(f"{PLOT_DIR}/age_box_descent.png")
    plt.close()

    return [
        f"{PLOT_DIR}/age_hist.png",
        f"{PLOT_DIR}/arrests_over_time.png",
        f"{PLOT_DIR}/gender_count.png",
        f"{PLOT_DIR}/age_box_descent.png"
    ]

def get_plot_images():
    plots = ["age_hist.png", "arrests_over_time.png", "gender_count.png", "age_box_descent.png"]
    paths = [os.path.join(PLOT_DIR, name) for name in plots]
    return paths