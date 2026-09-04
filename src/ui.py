from __future__ import annotations

import html

import pandas as pd
import streamlit as st


def inject_css() -> None:
    st.markdown(
        """
        <style>
        .block-container {padding-top: 1.6rem; padding-bottom: 2.5rem; max-width: 1500px;}
        .ola-title {font-size: 2.1rem; font-weight: 800; margin-bottom: .15rem;}
        .ola-subtitle {opacity: .72; margin-bottom: 1rem;}
        .metric-card {
            padding: 15px 16px; border: 1px solid rgba(255,255,255,.08);
            border-radius: 14px; background: rgba(255,255,255,.025);
            min-height: 102px;
        }
        .metric-label {font-size: .78rem; opacity: .65; margin-bottom: 7px;}
        .metric-value {font-size: 1.45rem; font-weight: 750;}
        .insight-card {
            padding: 14px 16px; border-left: 4px solid #16C784;
            border-radius: 10px; background: rgba(22,199,132,.07); margin: 6px 0;
        }
        .small-muted {font-size:.78rem; opacity:.62;}
        div[data-testid="stSidebar"] {border-right: 1px solid rgba(255,255,255,.08);}
        </style>
        """,
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str) -> None:
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{html.escape(label)}</div>'
        f'<div class="metric-value">{html.escape(value)}</div></div>',
        unsafe_allow_html=True,
    )


def insight(text: str) -> None:
    st.markdown(f'<div class="insight-card">{html.escape(text)}</div>', unsafe_allow_html=True)


def apply_sidebar_filters(df: pd.DataFrame) -> pd.DataFrame:
    st.sidebar.markdown("## Filters")
    filtered = df.copy()

    if "date" in filtered.columns and filtered["date"].notna().any():
        min_date = filtered["date"].min().date()
        max_date = filtered["date"].max().date()
        selected = st.sidebar.date_input(
            "Date range", value=(min_date, max_date), min_value=min_date, max_value=max_date
        )
        if isinstance(selected, tuple) and len(selected) == 2:
            start, end = selected
            filtered = filtered[(filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)]

    filters = [
        ("vehicle_type", "Vehicle type"),
        ("booking_status", "Booking status"),
        ("payment_method", "Payment method"),
        ("pickup_location", "Pickup location"),
    ]
    for col, label in filters:
        if col in filtered.columns:
            options = sorted(filtered[col].dropna().astype(str).unique().tolist())
            if options:
                selected = st.sidebar.multiselect(label, options, default=[])
                if selected:
                    filtered = filtered[filtered[col].astype(str).isin(selected)]

    st.sidebar.caption(f"Showing {len(filtered):,} of {len(df):,} rows")
    return filtered
