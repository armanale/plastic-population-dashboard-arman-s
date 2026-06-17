"""
filters.py - Filter and data processing functions for the Plastics Dashboard
"""

import pandas as pd
import numpy as np


def load_data(filepath: str = "data/plastics.csv") -> pd.DataFrame:
    """Load and clean the plastics dataset."""
    df = pd.read_csv(filepath)

    # Fill numeric NaNs with 0
    numeric_cols = ["empty", "hdpe", "ldpe", "o", "pet", "pp", "ps", "pvc", "grand_total", "volunteers"]
    df[numeric_cols] = df[numeric_cols].fillna(0)

    # Fill categorical NaN
    df["parent_company"] = df["parent_company"].fillna("Unknown")

    # Ensure correct types
    df["year"] = df["year"].astype(int)
    df["grand_total"] = df["grand_total"].astype(float)
    df["volunteers"] = df["volunteers"].astype(float)

    return df


def apply_filters(
    df: pd.DataFrame,
    selected_years: list,
    selected_countries: list,
    grand_total_range: tuple,
    search_keyword: str = "",
) -> pd.DataFrame:
    """Apply all sidebar filters and return filtered DataFrame."""
    filtered = df.copy()

    # Year filter
    if selected_years:
        filtered = filtered[filtered["year"].isin(selected_years)]

    # Country filter
    if selected_countries:
        filtered = filtered[filtered["country"].isin(selected_countries)]

    # Numerical range filter on grand_total
    filtered = filtered[
        (filtered["grand_total"] >= grand_total_range[0]) &
        (filtered["grand_total"] <= grand_total_range[1])
    ]

    # Text / search filter on parent_company or country
    if search_keyword.strip():
        kw = search_keyword.strip().lower()
        mask = (
            filtered["parent_company"].str.lower().str.contains(kw, na=False) |
            filtered["country"].str.lower().str.contains(kw, na=False)
        )
        filtered = filtered[mask]

    return filtered


def get_kpi_stats(df: pd.DataFrame) -> dict:
    """Compute top-level KPI summary cards."""
    # Exclude Grand Total aggregation rows for real stats
    real = df[df["parent_company"] != "Grand Total"]
    return {
        "total_records": len(real),
        "total_plastic": real["grand_total"].sum(),
        "avg_plastic_per_event": (real["grand_total"].sum() / real["num_events"].sum()) if real["num_events"].sum() > 0 else 0,
        "total_volunteers": real["volunteers"].sum(),
        "countries_covered": real["country"].nunique(),
        "companies_identified": real["parent_company"].nunique(),
    }


def get_plastic_type_totals(df: pd.DataFrame) -> pd.Series:
    """Aggregate totals for each plastic type."""
    real = df[df["parent_company"] != "Grand Total"]
    plastic_cols = {
        "HDPE": "hdpe",
        "LDPE": "ldpe",
        "Other": "o",
        "PET": "pet",
        "PP": "pp",
        "PS": "ps",
        "PVC": "pvc",
        "Empty/Unknown": "empty",
    }
    totals = {label: real[col].sum() for label, col in plastic_cols.items()}
    return pd.Series(totals).sort_values(ascending=False)


def get_top_polluters(df: pd.DataFrame, n: int = 10) -> pd.DataFrame:
    """Return top N companies by total plastic count (excluding Grand Total & Unbranded)."""
    real = df[(df["parent_company"] != "Grand Total") & (df["parent_company"] != "Unbranded")]
    return (
        real.groupby("parent_company")["grand_total"]
        .sum()
        .sort_values(ascending=False)
        .head(n)
        .reset_index()
        .rename(columns={"parent_company": "Company", "grand_total": "Total Plastic"})
    )


def get_country_totals(df: pd.DataFrame) -> pd.DataFrame:
    """Total plastic collected per country."""
    real = df[df["parent_company"] != "Grand Total"]
    return (
        real.groupby("country")["grand_total"]
        .sum()
        .sort_values(ascending=False)
        .reset_index()
        .rename(columns={"country": "Country", "grand_total": "Total Plastic"})
    )


def get_yearly_trend(df: pd.DataFrame) -> pd.DataFrame:
    """Yearly aggregation for line/area charts."""
    real = df[df["parent_company"] != "Grand Total"]
    yearly = real.groupby("year").agg(
        Total_Plastic=("grand_total", "sum"),
        Total_Volunteers=("volunteers", "sum"),
        Num_Events=("num_events", "sum"),
    ).reset_index()
    return yearly


def get_plastic_by_year(df: pd.DataFrame) -> pd.DataFrame:
    """Plastic type breakdown per year (for stacked area chart)."""
    real = df[df["parent_company"] != "Grand Total"]
    plastic_cols = ["hdpe", "ldpe", "o", "pet", "pp", "ps", "pvc", "empty"]
    label_map = {"hdpe": "HDPE", "ldpe": "LDPE", "o": "Other", "pet": "PET",
                 "pp": "PP", "ps": "PS", "pvc": "PVC", "empty": "Empty"}
    agg = real.groupby("year")[plastic_cols].sum().reset_index()
    agg = agg.rename(columns=label_map)
    return agg
