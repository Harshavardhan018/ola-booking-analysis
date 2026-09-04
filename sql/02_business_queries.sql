-- Queries I used while exploring the OLA booking data.
-- MySQL 8+

-- 1) Start with the overall picture
SELECT
    COUNT(*) AS total_bookings,
    SUM(booking_status = 'Successful') AS successful_bookings,
    ROUND(100.0 * SUM(booking_status = 'Successful') / COUNT(*), 2) AS success_rate_pct,
    ROUND(SUM(CASE WHEN booking_status = 'Successful' THEN booking_value ELSE 0 END), 2) AS successful_booking_value
FROM bookings;

-- 2) How are bookings split by status?
SELECT booking_status, COUNT(*) AS bookings
FROM bookings
GROUP BY booking_status
ORDER BY bookings DESC;

-- 3) Compare vehicle types
SELECT
    vehicle_type,
    COUNT(*) AS bookings,
    ROUND(AVG(booking_value), 2) AS avg_booking_value,
    ROUND(SUM(CASE WHEN booking_status = 'Successful' THEN booking_value ELSE 0 END), 2) AS successful_booking_value,
    ROUND(AVG(ride_distance), 2) AS avg_distance
FROM bookings
GROUP BY vehicle_type
ORDER BY successful_booking_value DESC;

-- 4) Reasons customers gave for cancelling
SELECT customer_cancel_reason, COUNT(*) AS cancellations
FROM bookings
WHERE customer_cancel_reason IS NOT NULL
  AND TRIM(customer_cancel_reason) <> ''
GROUP BY customer_cancel_reason
ORDER BY cancellations DESC;

-- 5) Reasons drivers gave for cancelling
SELECT driver_cancel_reason, COUNT(*) AS cancellations
FROM bookings
WHERE driver_cancel_reason IS NOT NULL
  AND TRIM(driver_cancel_reason) <> ''
GROUP BY driver_cancel_reason
ORDER BY cancellations DESC;

-- 6) Which hours get the most bookings?
SELECT HOUR(booking_time) AS booking_hour, COUNT(*) AS bookings
FROM bookings
GROUP BY HOUR(booking_time)
ORDER BY bookings DESC;

-- 7) Busiest pickup points
SELECT pickup_location, COUNT(*) AS bookings
FROM bookings
GROUP BY pickup_location
ORDER BY bookings DESC
LIMIT 10;

-- 8) Most common pickup -> drop routes
SELECT pickup_location, drop_location, COUNT(*) AS bookings
FROM bookings
GROUP BY pickup_location, drop_location
ORDER BY bookings DESC
LIMIT 10;

-- 9) Payment method share by booking value
SELECT
    payment_method,
    COUNT(*) AS bookings,
    ROUND(SUM(booking_value), 2) AS booking_value,
    ROUND(100.0 * SUM(booking_value) / SUM(SUM(booking_value)) OVER (), 2) AS value_share_pct
FROM bookings
GROUP BY payment_method
ORDER BY booking_value DESC;

-- 10) Daily bookings with a 7-day moving average
WITH daily_bookings AS (
    SELECT booking_date, COUNT(*) AS bookings
    FROM bookings
    GROUP BY booking_date
)
SELECT
    booking_date,
    bookings,
    ROUND(
        AVG(bookings) OVER (
            ORDER BY booking_date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ), 2
    ) AS bookings_7d_avg
FROM daily_bookings
ORDER BY booking_date;

-- 11) Rank vehicle types by successful booking value
WITH vehicle_value AS (
    SELECT
        vehicle_type,
        SUM(CASE WHEN booking_status = 'Successful' THEN booking_value ELSE 0 END) AS successful_value
    FROM bookings
    GROUP BY vehicle_type
)
SELECT
    vehicle_type,
    successful_value,
    DENSE_RANK() OVER (ORDER BY successful_value DESC) AS value_rank
FROM vehicle_value;

-- 12) Customers who booked more than once
SELECT
    customer_id,
    COUNT(*) AS total_bookings,
    SUM(booking_status = 'Successful') AS successful_bookings,
    ROUND(SUM(CASE WHEN booking_status = 'Successful' THEN booking_value ELSE 0 END), 2) AS successful_value
FROM bookings
GROUP BY customer_id
HAVING COUNT(*) > 1
ORDER BY total_bookings DESC, successful_value DESC;
