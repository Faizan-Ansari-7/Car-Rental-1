-- -- 1. USERS Table
-- CREATE TABLE users (
--     user_id VARCHAR(50) PRIMARY KEY,
--     first_name VARCHAR(50),
--     last_name VARCHAR(50),
--     email VARCHAR(100) UNIQUE NOT NULL,
--     phone_number VARCHAR(15),
--     password VARCHAR(100) NOT NULL,
--     role VARCHAR(20) DEFAULT 'Customer'
-- );

-- -- 2. CARS Table
-- CREATE TABLE cars (
--     car_id SERIAL PRIMARY KEY,
--     car_name VARCHAR(100) NOT NULL,
--     brand VARCHAR(50),
--     price_per_day DECIMAL(10, 2),
--     transmission VARCHAR(20),
--     fuel_type VARCHAR(20),
--     image_filename VARCHAR(255),
--     is_available BOOLEAN DEFAULT TRUE
-- );

-- -- 3. BOOKINGS Table
-- CREATE TABLE bookings (
--     booking_id SERIAL PRIMARY KEY,
--     car_id INT REFERENCES cars(car_id) ON DELETE CASCADE,
--     user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
--     start_date DATE NOT NULL,
--     end_date DATE NOT NULL,
--     total_amount DECIMAL(10, 2),
--     pickup_location VARCHAR(100),
--     status VARCHAR(20) DEFAULT 'Confirmed',
--     booking_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- 4. PAYMENTS Table
-- CREATE TABLE payments (
--     payment_id SERIAL PRIMARY KEY,
--     booking_id INT REFERENCES bookings(booking_id) ON DELETE CASCADE,
--     amount DECIMAL(10, 2) NOT NULL,
--     payment_method VARCHAR(50),
--     transaction_id VARCHAR(100) UNIQUE,
--     payment_status VARCHAR(20) DEFAULT 'Success',
--     payment_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- 5. FEEDBACK Table
-- CREATE TABLE feedback (
--     feedback_id SERIAL PRIMARY KEY,
--     user_id VARCHAR(50) REFERENCES users(user_id) ON DELETE CASCADE,
--     car_id INT REFERENCES cars(car_id) ON DELETE SET NULL,
--     rating INT CHECK (rating >= 1 AND rating <= 5),
--     comment TEXT,
--     created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
-- );

-- -- 6. CREATE DEFAULT ADMIN
-- INSERT INTO users (user_id, first_name, last_name, email, phone_number, password, role)
-- VALUES ('admin', 'System', 'Admin', 'admin@carfusion.com', '0000000000', 'admin123', 'Admin');

-- CREATE TABLE reviews (
--     review_id SERIAL PRIMARY KEY,
--     user_id VARCHAR(50),
--     car_id INT,
--     rating INT,
--     comment TEXT
-- );

-- ALTER TABLE bookings ADD COLUMN start_time TIME DEFAULT '10:00:00';
-- ALTER TABLE bookings ADD COLUMN end_time TIME DEFAULT '10:00:00';

-- -- 2. Add Quantity to Cars (Default 4 cars per model)
-- ALTER TABLE cars ADD COLUMN total_quantity INT DEFAULT 4;

-- ALTER TABLE cars ADD COLUMN IF NOT EXISTS total_quantity INT DEFAULT 4;

select * from users