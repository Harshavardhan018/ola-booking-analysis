-- OLA Bengaluru analytics table (MySQL 8+)
CREATE DATABASE IF NOT EXISTS ola_analytics;
USE ola_analytics;

CREATE TABLE IF NOT EXISTS bookings (
    booking_date DATE,
    booking_time TIME,
    booking_id VARCHAR(30) PRIMARY KEY,
    booking_status VARCHAR(80),
    customer_id VARCHAR(40),
    vehicle_type VARCHAR(50),
    pickup_location VARCHAR(120),
    drop_location VARCHAR(120),
    vehicle_tat DECIMAL(10,2),
    customer_tat DECIMAL(10,2),
    customer_cancel_reason VARCHAR(255),
    driver_cancel_reason VARCHAR(255),
    incomplete_rides VARCHAR(40),
    incomplete_reason VARCHAR(255),
    booking_value DECIMAL(12,2),
    payment_method VARCHAR(50),
    ride_distance DECIMAL(10,2),
    driver_rating DECIMAL(4,2),
    customer_rating DECIMAL(4,2)
);
