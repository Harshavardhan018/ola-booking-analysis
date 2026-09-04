from __future__ import annotations

import io
import re
from pathlib import Path
from typing import BinaryIO

import numpy as np
import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
LOCAL_DATA_PATH = PROJECT_ROOT / "data" / "Bengaluru_Ola_Booking_Data.csv"
REMOTE_DATA_URL = (
    "https://raw.githubusercontent.com/Satyam638/"
    "OLA_DataAnalyst_Project/main/Bengaluru_Ola_Booking_Data.csv"
)


def _slug(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return re.sub(r"_+", "_", value).strip("_")


ALIASES = {
    "date": "date",
    "time": "time",
    "booking_id": "booking_id",
    "booking_status": "booking_status",
    "customer_id": "customer_id",
    "vehicle_type": "vehicle_type",
    "pickup_location": "pickup_location",
    "drop_location": "drop_location",
    "v_tat": "vehicle_tat",
    "vtat": "vehicle_tat",
    "vehicle_tat": "vehicle_tat",
    "vehicle_time_to_arrive": "vehicle_tat",
    "c_tat": "customer_tat",
    "ctat": "customer_tat",
    "customer_tat": "customer_tat",
    "customer_time_to_arrive": "customer_tat",
    "canceled_rides_by_customer": "customer_cancel_reason",
    "cancelled_rides_by_customer": "customer_cancel_reason",
    "customer_cancellation_reason": "customer_cancel_reason",
    "canceled_rides_by_driver": "driver_cancel_reason",
    "cancelled_rides_by_driver": "driver_cancel_reason",
    "driver_cancellation_reason": "driver_cancel_reason",
    "incomplete_rides": "incomplete_rides",
    "incomplete_rides_reason": "incomplete_reason",
    "incomplete_ride_reason": "incomplete_reason",
    "booking_value": "booking_value",
    "payment_method": "payment_method",
    "ride_distance": "ride_distance",
    "driver_ratings": "driver_rating",
    "driver_rating": "driver_rating",
    "customer_rating": "customer_rating",
    "customer_ratings": "customer_rating",
}

NUMERIC_COLUMNS = [
    "vehicle_tat",
    "customer_tat",
    "booking_value",
    "ride_distance",
    "driver_rating",
    "customer_rating",
]


def standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Make the CSV headers consistent before the rest of the app uses them."""
    rename_map = {}
    for col in df.columns:
        key = _slug(str(col))
        rename_map[col] = ALIASES.get(key, key)
    return df.rename(columns=rename_map)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = standardize_columns(df.copy())

    for col in NUMERIC_COLUMNS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "date" in df.columns:
        df["date"] = pd.to_datetime(df["date"], errors="coerce", dayfirst=False)
        df["day"] = df["date"].dt.day_name()
        df["month"] = df["date"].dt.to_period("M").astype("string")
        df["is_weekend"] = df["date"].dt.dayofweek >= 5

    if "time" in df.columns:
        parsed_time = pd.to_datetime(df["time"].astype(str), errors="coerce")
        df["hour"] = parsed_time.dt.hour
    elif "date" in df.columns and pd.api.types.is_datetime64_any_dtype(df["date"]):
        df["hour"] = df["date"].dt.hour

    if "booking_status" in df.columns:
        status = df["booking_status"].astype("string").str.strip()
        status_l = status.str.lower()
        df["booking_status"] = status
        df["is_successful"] = status_l.str.contains("success", na=False)
        df["is_customer_cancel"] = status_l.str.contains("cancel", na=False) & status_l.str.contains("customer", na=False)
        df["is_driver_cancel"] = status_l.str.contains("cancel", na=False) & status_l.str.contains("driver", na=False)
        df["is_cancelled"] = status_l.str.contains("cancel", na=False)
        df["is_incomplete"] = status_l.str.contains("incomplete", na=False)
    else:
        df["is_successful"] = False
        df["is_customer_cancel"] = False
        df["is_driver_cancel"] = False
        df["is_cancelled"] = False
        df["is_incomplete"] = False

    if "pickup_location" in df.columns and "drop_location" in df.columns:
        df["route"] = (
            df["pickup_location"].astype("string").fillna("Unknown")
            + " → "
            + df["drop_location"].astype("string").fillna("Unknown")
        )

    return df


@st.cache_data(show_spinner=False, ttl=3600)
def _load_local_or_remote() -> tuple[pd.DataFrame, str]:
    if LOCAL_DATA_PATH.exists():
        return clean_data(pd.read_csv(LOCAL_DATA_PATH)), "Local CSV"
    try:
        return clean_data(pd.read_csv(REMOTE_DATA_URL)), "Upstream GitHub CSV"
    except Exception as exc:
        raise RuntimeError(
            "Could not load the dataset automatically. Download "
            "Bengaluru_Ola_Booking_Data.csv from the source repository and place it in data/."
        ) from exc


def load_data(uploaded_file: BinaryIO | None = None) -> tuple[pd.DataFrame, str]:
    if uploaded_file is not None:
        raw = uploaded_file.getvalue() if hasattr(uploaded_file, "getvalue") else uploaded_file.read()
        return clean_data(pd.read_csv(io.BytesIO(raw))), "Uploaded CSV"
    return _load_local_or_remote()
