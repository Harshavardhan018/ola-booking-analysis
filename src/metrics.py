from __future__ import annotations

import numpy as np
import pandas as pd


def safe_sum(df: pd.DataFrame, col: str) -> float:
    return float(df[col].sum(skipna=True)) if col in df.columns else 0.0


def safe_mean(df: pd.DataFrame, col: str) -> float:
    if col not in df.columns or df[col].dropna().empty:
        return 0.0
    return float(df[col].mean(skipna=True))


def rate(mask: pd.Series, total: int) -> float:
    if total == 0:
        return 0.0
    return float(mask.fillna(False).sum() / total * 100)


def headline_metrics(df: pd.DataFrame) -> dict[str, float]:
    total = len(df)
    successful = int(df.get("is_successful", pd.Series(False, index=df.index)).sum())
    cancelled = int(df.get("is_cancelled", pd.Series(False, index=df.index)).sum())
    customer_cancel = int(df.get("is_customer_cancel", pd.Series(False, index=df.index)).sum())
    driver_cancel = int(df.get("is_driver_cancel", pd.Series(False, index=df.index)).sum())

    revenue_df = df[df.get("is_successful", pd.Series(True, index=df.index))] if total else df
    revenue = safe_sum(revenue_df, "booking_value")

    return {
        "total_bookings": total,
        "successful_bookings": successful,
        "success_rate": successful / total * 100 if total else 0.0,
        "cancel_rate": cancelled / total * 100 if total else 0.0,
        "customer_cancel_rate": customer_cancel / total * 100 if total else 0.0,
        "driver_cancel_rate": driver_cancel / total * 100 if total else 0.0,
        "revenue": revenue,
        "avg_booking_value": safe_mean(revenue_df, "booking_value"),
        "avg_ride_distance": safe_mean(revenue_df, "ride_distance"),
        "avg_driver_rating": safe_mean(revenue_df, "driver_rating"),
        "avg_customer_rating": safe_mean(revenue_df, "customer_rating"),
    }


def top_value(df: pd.DataFrame, col: str, condition: pd.Series | None = None) -> tuple[str, int]:
    if col not in df.columns:
        return "N/A", 0
    base = df if condition is None else df[condition]
    series = base[col].dropna().astype(str)
    if series.empty:
        return "N/A", 0
    counts = series.value_counts()
    return str(counts.index[0]), int(counts.iloc[0])
