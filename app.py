import os
from pathlib import Path
from urllib.parse import quote_plus

import pandas as pd
import plotly.express as px
import streamlit as st


# --------------------------------------------------
# Page settings
# --------------------------------------------------
st.set_page_config(
    page_title="OLA Booking Analysis",
    page_icon="🚕",
    layout="wide"
)

PROJECT_ROOT = Path(__file__).resolve().parent
DATA_PATH = PROJECT_ROOT / "data" / "Bengaluru_Ola_Booking_Data.csv"

SQL_QUERY = """
SELECT
    booking_date AS date,
    booking_time AS time,
    booking_id,
    booking_status,
    customer_id,
    vehicle_type,
    pickup_location,
    drop_location,
    vehicle_tat AS v_tat,
    customer_tat AS c_tat,
    customer_cancel_reason AS cancelled_rides_by_customer,
    driver_cancel_reason AS cancelled_rides_by_driver,
    incomplete_rides,
    incomplete_reason,
    booking_value,
    payment_method,
    ride_distance,
    driver_rating AS driver_ratings,
    customer_rating
FROM dbo.bookings
"""


def _sql_setting(name, default=None):
    """Read SQL settings from environment variables or Streamlit secrets."""
    environment_name = f"OLA_SQL_{name.upper()}"
    environment_value = os.getenv(environment_name)
    if environment_value:
        return environment_value

    try:
        return st.secrets.get("sql_server", {}).get(name, default)
    except Exception:
        return default


def _sql_server_url():
    connection_string = _sql_setting("connection_string")
    if connection_string:
        return connection_string

    server = _sql_setting("server")
    database = _sql_setting("database", "ola_analytics")
    driver = _sql_setting("driver", "ODBC Driver 18 for SQL Server")
    trusted = str(_sql_setting("trusted_connection", "false")).lower() in {
        "1", "true", "yes"
    }

    if not server:
        raise ValueError(
            "SQL Server is selected, but no server is configured. "
            "Set OLA_SQL_SERVER or sql_server.server in .streamlit/secrets.toml."
        )

    if trusted:
        odbc_options = (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            "Trusted_Connection=yes;TrustServerCertificate=yes;"
        )
    else:
        username = _sql_setting("username")
        password = _sql_setting("password")
        if not username or not password:
            raise ValueError(
                "SQL authentication requires sql_server.username and "
                "sql_server.password."
            )
        odbc_options = (
            f"DRIVER={{{driver}}};SERVER={server};DATABASE={database};"
            f"UID={username};PWD={password};TrustServerCertificate=yes;"
        )

    return "mssql+pyodbc:///?odbc_connect=" + quote_plus(odbc_options)


# --------------------------------------------------
# Load and clean data
# --------------------------------------------------
@st.cache_data
def load_data():
    source = os.getenv("OLA_DATA_SOURCE", "csv").lower()
    if source == "sqlserver":
        from sqlalchemy import create_engine, text

        engine = create_engine(_sql_server_url(), pool_pre_ping=True)
        with engine.connect() as connection:
            df = pd.read_sql(text(SQL_QUERY), connection)
    else:
        df = pd.read_csv(DATA_PATH)

    # Make column names easy to work with in Python
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(" ", "_")
        .str.replace("-", "_")
    )

    # Handle small column-name differences
    df = df.rename(columns={
        "canceled_rides_by_customer": "cancelled_rides_by_customer",
        "canceled_rides_by_driver": "cancelled_rides_by_driver",
        "driver_rating": "driver_ratings",
        "customer_ratings": "customer_rating"
    })

    # Convert date column
    df["date"] = pd.to_datetime(
        df["date"],
        errors="coerce"
    )

    # Extract hour from time
    time_value = pd.to_datetime(
        df["time"].astype(str),
        errors="coerce"
    )

    df["hour"] = time_value.dt.hour

    # Convert important columns to numeric
    numeric_columns = [
        "booking_value",
        "ride_distance",
        "driver_ratings",
        "customer_rating",
        "v_tat",
        "c_tat"
    ]

    for column in numeric_columns:
        if column in df.columns:
            df[column] = pd.to_numeric(
                df[column],
                errors="coerce"
            )

    # Create useful flags for analysis
    status = (
        df["booking_status"]
        .fillna("")
        .str.lower()
    )

    df["is_successful"] = (
        status.str.contains("success")
    )

    df["customer_cancelled"] = (
        status.str.contains("customer")
        & status.str.contains("cancel")
    )

    df["driver_cancelled"] = (
        status.str.contains("driver")
        & status.str.contains("cancel")
    )

    # Create weekday column
    df["weekday"] = (
        df["date"]
        .dt.day_name()
    )

    # Create route column
    df["route"] = (
        df["pickup_location"].astype(str)
        + " → "
        + df["drop_location"].astype(str)
    )

    return df


# --------------------------------------------------
# Read dataset
# --------------------------------------------------
try:
    df = load_data()

except FileNotFoundError:

    st.error(
        "Dataset not found. "
        "Please keep Bengaluru_Ola_Booking_Data.csv "
        "inside the data folder."
    )

    st.stop()


# --------------------------------------------------
# Dashboard heading
# --------------------------------------------------
st.title("🚕 OLA Booking Analysis")

st.caption(
    "An interactive analysis of Bengaluru ride bookings "
    "using Python, Pandas, Plotly and Streamlit."
)


# --------------------------------------------------
# Sidebar filters
# --------------------------------------------------
st.sidebar.header("Filters")


# Date filter
min_date = df["date"].min().date()
max_date = df["date"].max().date()

date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)


# Vehicle filter
vehicle_list = sorted(
    df["vehicle_type"]
    .dropna()
    .unique()
)

selected_vehicles = st.sidebar.multiselect(
    "Vehicle type",
    vehicle_list,
    default=vehicle_list
)


# Booking status filter
status_list = sorted(
    df["booking_status"]
    .dropna()
    .unique()
)

selected_status = st.sidebar.multiselect(
    "Booking status",
    status_list,
    default=status_list
)


# Payment filter
payment_list = sorted(
    df["payment_method"]
    .dropna()
    .unique()
)

selected_payment = st.sidebar.multiselect(
    "Payment method",
    payment_list,
    default=payment_list
)


# --------------------------------------------------
# Apply filters
# --------------------------------------------------
filtered_df = df.copy()


if len(date_range) == 2:

    start_date, end_date = date_range

    filtered_df = filtered_df[
        filtered_df["date"]
        .dt.date
        .between(
            start_date,
            end_date
        )
    ]


filtered_df = filtered_df[
    filtered_df["vehicle_type"]
    .isin(selected_vehicles)
]


filtered_df = filtered_df[
    filtered_df["booking_status"]
    .isin(selected_status)
]


filtered_df = filtered_df[
    filtered_df["payment_method"]
    .isin(selected_payment)
]


if filtered_df.empty:

    st.warning(
        "No data available for the selected filters."
    )

    st.stop()


# --------------------------------------------------
# KPI calculations
# --------------------------------------------------
total_bookings = len(filtered_df)


successful_df = filtered_df[
    filtered_df["is_successful"]
]


successful_bookings = len(
    successful_df
)


success_rate = (
    successful_bookings
    / total_bookings
) * 100


successful_booking_value = (
    successful_df["booking_value"]
    .sum()
)


average_booking_value = (
    successful_df["booking_value"]
    .mean()
)


average_distance = (
    successful_df["ride_distance"]
    .mean()
)


customer_cancellations = int(
    filtered_df["customer_cancelled"]
    .sum()
)


driver_cancellations = int(
    filtered_df["driver_cancelled"]
    .sum()
)


# --------------------------------------------------
# KPI cards
# --------------------------------------------------
kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)


kpi1.metric(
    "Total Bookings",
    f"{total_bookings:,}"
)


kpi2.metric(
    "Successful Bookings",
    f"{successful_bookings:,}"
)


kpi3.metric(
    "Success Rate",
    f"{success_rate:.1f}%"
)


kpi4.metric(
    "Successful Booking Value",
    f"₹{successful_booking_value:,.0f}"
)


kpi5.metric(
    "Avg. Ride Distance",
    f"{average_distance:.1f} km"
)


# --------------------------------------------------
# Dashboard tabs
# --------------------------------------------------
overview_tab, demand_tab, cancel_tab, vehicle_tab, data_tab = st.tabs(
    [
        "Overview",
        "Demand",
        "Cancellations",
        "Vehicles & Value",
        "Raw Data"
    ]
)


# ==================================================
# OVERVIEW TAB
# ==================================================
with overview_tab:

    st.subheader(
        "Overall Booking Performance"
    )

    left, right = st.columns(2)


    # Daily booking trend
    daily_bookings = (
        filtered_df
        .groupby("date")
        .size()
        .reset_index(
            name="bookings"
        )
    )


    with left:

        fig = px.line(
            daily_bookings,
            x="date",
            y="bookings",
            markers=True,
            title="Daily Booking Trend"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Booking status
    status_count = (
        filtered_df[
            "booking_status"
        ]
        .value_counts()
        .reset_index()
    )

    status_count.columns = [
        "booking_status",
        "bookings"
    ]


    with right:

        fig = px.pie(
            status_count,
            names="booking_status",
            values="bookings",
            hole=0.45,
            title="Booking Status Distribution"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Vehicle booking count
    vehicle_count = (
        filtered_df[
            "vehicle_type"
        ]
        .value_counts()
        .reset_index()
    )

    vehicle_count.columns = [
        "vehicle_type",
        "bookings"
    ]


    fig = px.bar(
        vehicle_count,
        x="vehicle_type",
        y="bookings",
        title="Bookings by Vehicle Type"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# DEMAND TAB
# ==================================================
with demand_tab:

    st.subheader(
        "Booking Demand Analysis"
    )

    left, right = st.columns(2)


    # Bookings by hour
    hourly = (
        filtered_df
        .groupby("hour")
        .size()
        .reset_index(
            name="bookings"
        )
    )


    with left:

        fig = px.bar(
            hourly,
            x="hour",
            y="bookings",
            title="Bookings by Hour"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Bookings by weekday
    weekday = (
        filtered_df[
            "weekday"
        ]
        .value_counts()
        .reindex(
            [
                "Monday",
                "Tuesday",
                "Wednesday",
                "Thursday",
                "Friday",
                "Saturday",
                "Sunday"
            ]
        )
        .reset_index()
    )


    weekday.columns = [
        "weekday",
        "bookings"
    ]


    with right:

        fig = px.bar(
            weekday,
            x="weekday",
            y="bookings",
            title="Bookings by Day"
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Top pickup locations
    pickup_locations = (
        filtered_df[
            "pickup_location"
        ]
        .value_counts()
        .head(10)
        .reset_index()
    )


    pickup_locations.columns = [
        "pickup_location",
        "bookings"
    ]


    fig = px.bar(
        pickup_locations.sort_values(
            "bookings"
        ),
        x="bookings",
        y="pickup_location",
        orientation="h",
        title="Top 10 Pickup Locations"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


# ==================================================
# CANCELLATION TAB
# ==================================================
with cancel_tab:

    st.subheader(
        "Cancellation Analysis"
    )


    total_cancellations = (
        customer_cancellations
        + driver_cancellations
    )


    cancellation_rate = (
        total_cancellations
        / total_bookings
    ) * 100


    c1, c2, c3 = st.columns(3)


    c1.metric(
        "Customer Cancellations",
        f"{customer_cancellations:,}"
    )


    c2.metric(
        "Driver Cancellations",
        f"{driver_cancellations:,}"
    )


    c3.metric(
        "Cancellation Rate",
        f"{cancellation_rate:.1f}%"
    )


    left, right = st.columns(2)


    # Customer cancellation reasons
    if "cancelled_rides_by_customer" in filtered_df.columns:

        customer_reasons = (
            filtered_df[
                "cancelled_rides_by_customer"
            ]
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )


        customer_reasons.columns = [
            "reason",
            "rides"
        ]


        with left:

            fig = px.bar(
                customer_reasons.sort_values(
                    "rides"
                ),
                x="rides",
                y="reason",
                orientation="h",
                title="Customer Cancellation Reasons"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


    # Driver cancellation reasons
    if "cancelled_rides_by_driver" in filtered_df.columns:

        driver_reasons = (
            filtered_df[
                "cancelled_rides_by_driver"
            ]
            .dropna()
            .value_counts()
            .head(10)
            .reset_index()
        )


        driver_reasons.columns = [
            "reason",
            "rides"
        ]


        with right:

            fig = px.bar(
                driver_reasons.sort_values(
                    "rides"
                ),
                x="rides",
                y="reason",
                orientation="h",
                title="Driver Cancellation Reasons"
            )

            st.plotly_chart(
                fig,
                use_container_width=True
            )


# ==================================================
# VEHICLE & VALUE TAB
# ==================================================
with vehicle_tab:

    st.subheader(
        "Vehicle and Booking Value Analysis"
    )


    vehicle_summary = (
        successful_df
        .groupby(
            "vehicle_type"
        )
        .agg(
            successful_rides=(
                "booking_id",
                "count"
            ),
            booking_value=(
                "booking_value",
                "sum"
            ),
            average_value=(
                "booking_value",
                "mean"
            ),
            average_distance=(
                "ride_distance",
                "mean"
            )
        )
        .reset_index()
    )


    left, right = st.columns(2)


    with left:

        fig = px.bar(
            vehicle_summary,
            x="vehicle_type",
            y="booking_value",
            title=(
                "Successful Booking Value "
                "by Vehicle Type"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    with right:

        fig = px.bar(
            vehicle_summary,
            x="vehicle_type",
            y="average_distance",
            title=(
                "Average Ride Distance "
                "by Vehicle Type"
            )
        )

        st.plotly_chart(
            fig,
            use_container_width=True
        )


    # Payment methods
    payment_summary = (
        successful_df[
            "payment_method"
        ]
        .value_counts()
        .reset_index()
    )


    payment_summary.columns = [
        "payment_method",
        "rides"
    ]


    fig = px.pie(
        payment_summary,
        names="payment_method",
        values="rides",
        title="Payment Method Usage"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.subheader(
        "Vehicle Summary"
    )


    st.dataframe(
        vehicle_summary.round(2),
        use_container_width=True,
        hide_index=True
    )


# ==================================================
# RAW DATA TAB
# ==================================================
with data_tab:

    st.subheader(
        "Filtered Booking Records"
    )


    st.write(
        f"Rows after filtering: "
        f"**{len(filtered_df):,}**"
    )


    st.dataframe(
        filtered_df,
        use_container_width=True,
        hide_index=True,
        height=500
    )


    csv = (
        filtered_df
        .to_csv(
            index=False
        )
        .encode(
            "utf-8"
        )
    )


    st.download_button(
        "Download Filtered Data",
        csv,
        "ola_filtered_data.csv",
        "text/csv"
    )