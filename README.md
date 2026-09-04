# OLA Booking Analysis

An interactive Streamlit dashboard and SQL analysis project built around OLA ride-booking data from Bengaluru. It helps explore booking performance, demand patterns, cancellations, vehicle mix, booking value, payment methods, and filtered records.

## What This Project Includes

- A CSV-first Streamlit dashboard with optional Microsoft SQL Server loading.
- Data cleaning and derived fields for successful bookings, cancellation types, hour, weekday, and route.
- Interactive filters for date range, vehicle type, booking status, and payment method.
- MySQL and SQL Server table definitions plus business-focused SQL queries.
- CSV download for the currently filtered dashboard data.

## Dashboard

The dashboard is organized into five tabs:

### Overview

- Total bookings
- Successful bookings
- Success rate
- Successful booking value
- Average successful ride distance
- Daily booking trend
- Booking-status distribution
- Bookings by vehicle type

### Demand

- Bookings by hour
- Bookings by weekday
- Top pickup locations

### Cancellations

- Customer and driver cancellation counts
- Combined cancellation rate
- Customer cancellation reasons
- Driver cancellation reasons

### Vehicles & Value

- Successful booking value by vehicle type
- Average successful ride distance by vehicle type
- Payment-method distribution
- Vehicle summary table

### Raw Data

View the filtered records and download them as a CSV file.

## Technology

- Python
- Pandas and NumPy
- Streamlit
- Plotly
- SQLAlchemy and `pyodbc` for SQL Server connectivity
- MySQL 8+ and Microsoft SQL Server scripts

## Project Structure

```text
ola_streamlit_analytics/
|-- app.py                              # Streamlit dashboard entry point
|-- requirements.txt                    # Python dependencies
|-- PROJECT_STRUCTURE.md                # Project notes
|-- data/
|   `-- Bengaluru_Ola_Booking_Data.csv  # Local dashboard dataset
|-- sql/
|   |-- 01_create_table.sql             # MySQL table definition
|   |-- 01_create_table_sqlserver.sql   # SQL Server table definition
|   |-- 02_business_queries.sql         # Business analysis queries
|   `-- insert_bookings.sql              # MySQL data import script
|-- src/
|   |-- data_loader.py                  # Reusable loading and cleaning helpers
|   |-- metrics.py                      # Reusable KPI helpers
|   `-- ui.py                           # Reusable UI helpers
`-- .streamlit/config.toml              # Streamlit theme configuration
```

`app.py` is the current executable dashboard. The modules in `src/` contain reusable loading, metric, and UI helpers for further modularization.

## Quick Start

From the project directory:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

The dashboard opens at `http://localhost:8501`.

The included CSV is loaded automatically from `data/Bengaluru_Ola_Booking_Data.csv`. If the file is missing, add a compatible CSV at that path before starting the app.

## SQL Server Data Source

The default source is the local CSV. To load the dashboard from SQL Server:

1. Run `sql/01_create_table_sqlserver.sql` in SQL Server.
2. Import the booking data into `ola_analytics.dbo.bookings`.
3. Install Microsoft ODBC Driver 18 for SQL Server.
4. Create `.streamlit/secrets.toml` with local connection settings:

```toml
[sql_server]
server = "localhost\\SQLEXPRESS"
database = "ola_analytics"
trusted_connection = true
driver = "ODBC Driver 18 for SQL Server"
```

5. Start the app with:

```powershell
$env:OLA_DATA_SOURCE = "sqlserver"
python -m streamlit run app.py
```

For SQL authentication, set `trusted_connection = false` and provide `username` and `password`. Never commit `secrets.toml`; it is excluded by `.gitignore`.

To return to CSV mode:

```powershell
$env:OLA_DATA_SOURCE = "csv"
python -m streamlit run app.py
```

The app also accepts `OLA_SQL_*` environment variables for SQL Server settings. See `_sql_setting` in `app.py` for the supported names.

## SQL Analysis

`sql/02_business_queries.sql` covers:

- Booking totals, success rate, and successful booking value
- Booking-status distribution
- Vehicle-type performance
- Customer and driver cancellation reasons
- Peak booking hours
- Busiest pickup locations and routes
- Payment-method share by booking value
- Daily bookings with a seven-day moving average
- Vehicle ranking by successful booking value
- Repeat customers

The business queries and import script use MySQL syntax. Use the SQL Server table definition for the dashboard's SQL Server connection.

## Dataset

The project uses the Bengaluru OLA booking dataset from [Satyam638/OLA_DataAnalyst_Project](https://github.com/Satyam638/OLA_DataAnalyst_Project). It is included locally for reproducible dashboard runs and is used for learning and portfolio analysis.

## Validation

```powershell
python -m py_compile app.py src\data_loader.py src\metrics.py src\ui.py
```

## License and Attribution

This repository is an educational portfolio project. Review the upstream dataset repository for the dataset's original terms and attribution requirements.
