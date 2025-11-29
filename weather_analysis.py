"""
Weather Data Visualizer - Mini Project
Author: Tanishq
Course: Programming for Problem Solving using Python
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


# =========================
#  Utility / Setup
# =========================

def ensure_directories():
    """Ensure data and plots folders exist."""
    os.makedirs("data", exist_ok=True)
    os.makedirs("plots", exist_ok=True)


def load_data(filepath: str) -> pd.DataFrame:
    """
    Task 1: Load CSV into a DataFrame and do basic inspection.
    """
    print(f"Loading data from: {filepath}")
    df = pd.read_csv(filepath)

    # Strip spaces from column names like " _tempm"
    df.columns = df.columns.str.strip()

    print("\n--- HEAD ---")
    print(df.head())
    print("\n--- INFO ---")
    print(df.info())
    print("\n--- DESCRIBE (numeric) ---")
    print(df.describe(include="all"))

    return df


# =========================
#  Task 2: Cleaning
# =========================

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the weather data:
    - Convert datetime_utc to datetime
    - Convert numeric columns
    - Handle missing values
    - Create extra columns for date, month, year
    """
    # Convert datetime column
    df["datetime_utc"] = pd.to_datetime(df["datetime_utc"], errors="coerce")

    # Drop rows with invalid datetime
    df = df.dropna(subset=["datetime_utc"])

    # Numeric columns in your header
    numeric_cols = [
        "_dewptm", "_heatindexm", "_hum", "_precipm", "_pressurem",
        "_tempm", "_vism", "_wdird", "_wgustm", "_windchillm", "_wspdm"
    ]

    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    # Boolean / indicator columns (0/1)
    bool_cols = ["_fog", "_hail", "_rain", "_snow", "_thunder", "_tornado"]
    for col in bool_cols:
        if col in df.columns:
            # Coerce to numeric, then fill NaN with 0 and convert to int
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    # Handle missing numeric values: fill with column mean
    df[numeric_cols] = df[numeric_cols].apply(lambda s: s.fillna(s.mean()))

    # Create date-based helper columns
    df["date"] = df["datetime_utc"].dt.date
    df["year"] = df["datetime_utc"].dt.year
    df["month"] = df["datetime_utc"].dt.month
    df["day"] = df["datetime_utc"].dt.day

    # Optional: create a month_name column for nicer plots
    df["month_name"] = df["datetime_utc"].dt.month_name()

    print("\n--- AFTER CLEANING ---")
    print(df.head())
    print(df.describe(include="all"))

    return df


# =========================
#  Task 3: Statistical Analysis with NumPy
# =========================

def compute_statistics(df: pd.DataFrame) -> dict:
    """
    Compute daily, monthly, and yearly statistics using NumPy.
    Returns a dictionary of summary DataFrames.
    """

    # Daily stats (group by date)
    daily = df.groupby("date")["_tempm"].agg(
        daily_mean=np.mean,
        daily_min=np.min,
        daily_max=np.max,
        daily_std=np.std
    )

    # Monthly stats (group by year & month)
    monthly = df.groupby(["year", "month"])["_tempm"].agg(
        monthly_mean=np.mean,
        monthly_min=np.min,
        monthly_max=np.max,
        monthly_std=np.std
    )

    # Yearly stats
    yearly = df.groupby("year")["_tempm"].agg(
        yearly_mean=np.mean,
        yearly_min=np.min,
        yearly_max=np.max,
        yearly_std=np.std
    )

    print("\n--- DAILY STATS (Temperature) ---")
    print(daily.head())
    print("\n--- MONTHLY STATS (Temperature) ---")
    print(monthly.head())
    print("\n--- YEARLY STATS (Temperature) ---")
    print(yearly.head())

    stats = {
        "daily_temp_stats": daily,
        "monthly_temp_stats": monthly,
        "yearly_temp_stats": yearly
    }

    return stats


# =========================
#  Task 4: Visualization
# =========================

def plot_daily_temperature(df: pd.DataFrame, output_path="plots/daily_temperature.png"):
    """Line chart for daily average temperature trends."""
    daily = df.groupby("date")["_tempm"].mean()

    plt.figure()
    plt.plot(daily.index, daily.values)
    plt.xlabel("Date")
    plt.ylabel("Average Temperature (°C)")
    plt.title("Daily Average Temperature Trend")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_monthly_rainfall(df, output_path="plots/monthly_rainfall.png"):
    """
    Improved rainfall plot:
    - Uses month names instead of long YYYY-MM
    - Handles missing/zero rainfall gracefully
    - Falls back to counting rainy days if no rainfall values exist
    """

    # Case 1: If rainfall column missing entirely
    if "_precipm" not in df.columns:
        print("No _precipm column found for rainfall plot.")
        return

    # Monthly total rainfall
    monthly = df.groupby("month")["_precipm"].sum().reset_index()

    # If all rainfall = 0, rainfall dataset is empty/useless
    if monthly["_precipm"].sum() == 0:
        print("Rainfall values are all zero → switching to 'rainy days count'.")

        rainy_days = df.groupby("month")["_rain"].sum().reset_index()
        rainy_days["month_name"] = pd.to_datetime(rainy_days["month"], format="%m").dt.month_name()

        plt.figure(figsize=(10, 5))
        plt.bar(rainy_days["month_name"], rainy_days["_rain"])
        plt.title("Rainy Days per Month")
        plt.xlabel("Month")
        plt.ylabel("Rainy Days Count")
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(output_path)
        plt.close()
        print(f"Saved (Rainy Days): {output_path}")
        return

    # Normal rainfall case
    monthly["month_name"] = pd.to_datetime(monthly["month"], format="%m").dt.month_name()

    plt.figure(figsize=(10, 5))
    plt.bar(monthly["month_name"], monthly["_precipm"])
    plt.xlabel("Month")
    plt.ylabel("Total Rainfall (mm)")
    plt.title("Monthly Rainfall Totals")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_humidity_vs_temperature(df: pd.DataFrame, output_path="plots/humidity_vs_temperature.png"):
    """Scatter plot for humidity vs temperature."""
    plt.figure()
    plt.scatter(df["_tempm"], df["_hum"])
    plt.xlabel("Temperature (°C)")
    plt.ylabel("Humidity (%)")
    plt.title("Humidity vs Temperature")
    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


def plot_combined(df: pd.DataFrame, output_path="plots/combined_plots.png"):
    """
    Combine at least two plots in a single figure.
    Example: temperature and humidity daily averages.
    """
    daily = df.groupby("date").agg(
        temp_mean=("_tempm", "mean"),
        hum_mean=("_hum", "mean")
    )

    fig, axes = plt.subplots(2, 1, figsize=(10, 8))

    # Subplot 1: temperature
    axes[0].plot(daily.index, daily["temp_mean"])
    axes[0].set_title("Daily Average Temperature")
    axes[0].set_xlabel("Date")
    axes[0].set_ylabel("Temperature (°C)")
    axes[0].tick_params(axis="x", rotation=45)

    # Subplot 2: humidity
    axes[1].plot(daily.index, daily["hum_mean"])
    axes[1].set_title("Daily Average Humidity")
    axes[1].set_xlabel("Date")
    axes[1].set_ylabel("Humidity (%)")
    axes[1].tick_params(axis="x", rotation=45)

    plt.tight_layout()
    plt.savefig(output_path)
    plt.close()
    print(f"Saved: {output_path}")


# =========================
#  Task 5: Grouping & Aggregation
# =========================

def month_to_season(month: int) -> str:
    """Simple season mapping for India-like climate."""
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon"


def compute_grouped_stats(df: pd.DataFrame) -> dict:
    """
    Group data by month and season and calculate aggregate statistics.
    """
    # Group by month
    monthly_group = df.groupby("month").agg(
        avg_temp=("_tempm", "mean"),
        avg_hum=("_hum", "mean"),
        total_rain=("_precipm", "sum")
    )

    # Season column
    df["season"] = df["month"].apply(month_to_season)

    season_group = df.groupby("season").agg(
        avg_temp=("_tempm", "mean"),
        avg_hum=("_hum", "mean"),
        total_rain=("_precipm", "sum")
    )

    print("\n--- GROUPED BY MONTH ---")
    print(monthly_group)
    print("\n--- GROUPED BY SEASON ---")
    print(season_group)

    return {
        "monthly_group": monthly_group,
        "season_group": season_group
    }


# =========================
#  Task 6: Export & Storytelling
# =========================

def export_cleaned_data(df: pd.DataFrame, output_path="data/cleaned_weather.csv"):
    """Export cleaned data to new CSV file."""
    df.to_csv(output_path, index=False)
    print(f"Cleaned data exported to: {output_path}")


def generate_text_report(stats: dict, grouped: dict, output_path="report.md"):
    """
    Generate a simple Markdown report summarizing insights.
    You can edit this file later for better storytelling.
    """
    yearly = stats["yearly_temp_stats"]
    season_group = grouped["season_group"]

    with open(output_path, "w", encoding="utf-8") as f:
        f.write("# Weather Data Analysis Report\n\n")
        f.write("This report summarizes key insights from the weather dataset.\n\n")

        # Yearly temperature summary
        f.write("## Yearly Temperature Summary\n\n")
        f.write("Below are the yearly average, minimum, and maximum temperatures.\n\n")
        f.write(yearly.to_markdown())
        f.write("\n\n")

        # Seasonal summary
        f.write("## Seasonal Summary\n\n")
        f.write(
            "The table below shows average temperature, humidity, and total rainfall for each season.\n\n"
        )
        f.write(season_group.to_markdown())
        f.write("\n\n")

        f.write("## Observations (You can expand this section)\n\n")
        f.write("- Identify the hottest and coldest years.\n")
        f.write("- Describe which season has the highest rainfall.\n")
        f.write("- Comment on the relationship between humidity and temperature.\n")

    print(f"Report generated at: {output_path}")


# =========================
#  Main Runner
# =========================

def main():
    ensure_directories()

    # Task 1: Load
    raw_path = "data/raw_weather.csv"  # make sure your file is here
    df = load_data(raw_path)

    # Task 2: Clean
    df_clean = clean_data(df)

    # Task 3: Statistical analysis
    stats = compute_statistics(df_clean)

    # Task 4: Visualization
    plot_daily_temperature(df_clean)
    plot_monthly_rainfall(df_clean)
    plot_humidity_vs_temperature(df_clean)
    plot_combined(df_clean)

    # Task 5: Grouping & aggregation
    grouped = compute_grouped_stats(df_clean)

    # Task 6: Export & storytelling
    export_cleaned_data(df_clean)
    generate_text_report(stats, grouped)

    print("\nAll tasks completed successfully!")


if __name__ == "__main__":
    main()
