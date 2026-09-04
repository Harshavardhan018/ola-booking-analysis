# Project notes

I kept the project small enough to understand without jumping through too many files.

## `app.py`
This is where the Streamlit pages are put together. It contains the charts and the layout for the six dashboard tabs.

## `src/data_loader.py`
Reads the CSV, cleans column names, converts dates/numeric fields and creates a few helper columns such as `is_successful`, `is_cancelled`, `hour`, `day` and `route`.

## `src/metrics.py`
Contains the small KPI calculations used at the top of the dashboard. Keeping them here avoids repeating the same calculation inside chart code.

## `src/ui.py`
Contains the sidebar filters and the small bits of styling used for KPI and note cards.

## `sql/`
SQL versions of the questions explored in the dashboard. These are useful for practising the analysis without Pandas.

## `data/`
The CSV belongs here as `Bengaluru_Ola_Booking_Data.csv`. The actual dataset is not duplicated in this package by default; keep the original source credit when you add it.
