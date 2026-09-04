-- SQL Server version of the OLA analytics table.
-- Run this in the ola_analytics database before importing the CSV.

IF DB_ID(N'ola_analytics') IS NULL
    CREATE DATABASE ola_analytics;
GO

USE ola_analytics;
GO

IF OBJECT_ID(N'dbo.bookings', N'U') IS NULL
BEGIN
    CREATE TABLE dbo.bookings (
        booking_date date,
        booking_time time,
        booking_id varchar(30) NOT NULL PRIMARY KEY,
        booking_status varchar(80),
        customer_id varchar(40),
        vehicle_type varchar(50),
        pickup_location varchar(120),
        drop_location varchar(120),
        vehicle_tat decimal(10, 2),
        customer_tat decimal(10, 2),
        customer_cancel_reason varchar(255),
        driver_cancel_reason varchar(255),
        incomplete_rides varchar(40),
        incomplete_reason varchar(255),
        booking_value decimal(12, 2),
        payment_method varchar(50),
        ride_distance decimal(10, 2),
        driver_rating decimal(4, 2),
        customer_rating decimal(4, 2)
    );
END;
GO