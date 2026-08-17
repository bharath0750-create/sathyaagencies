CREATE DATABASE IF NOT EXISTS sathya_agencies CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE sathya_agencies;

CREATE TABLE IF NOT EXISTS users (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 email VARCHAR(160) NOT NULL UNIQUE,
 phone VARCHAR(20) NOT NULL,
 password_hash VARCHAR(255) NOT NULL,
 address VARCHAR(255),
 city VARCHAR(100),
 pincode VARCHAR(10),
 role ENUM('user','admin') NOT NULL DEFAULT 'user',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS gases (
 id INT AUTO_INCREMENT PRIMARY KEY,
 gas_name VARCHAR(100) NOT NULL,
 description TEXT,
 cylinder_size VARCHAR(20) NOT NULL DEFAULT '10L',
 available_quantity INT NOT NULL DEFAULT 0,
 status ENUM('Available','Unavailable') NOT NULL DEFAULT 'Available'
);

CREATE TABLE IF NOT EXISTS bookings (
 id INT AUTO_INCREMENT PRIMARY KEY,
 booking_id VARCHAR(30) NOT NULL UNIQUE,
 user_id INT NOT NULL,
 gas_id INT NOT NULL,
 quantity INT NOT NULL,
 cylinder_size VARCHAR(20) NOT NULL,
 customer_name VARCHAR(120) NOT NULL,
 phone VARCHAR(20) NOT NULL,
 email VARCHAR(160) NOT NULL,
 address VARCHAR(255) NOT NULL,
 city VARCHAR(100) NOT NULL,
 pincode VARCHAR(10) NOT NULL,
 payment_method VARCHAR(40) NOT NULL DEFAULT 'Cash on Delivery',
 booking_status ENUM('Pending','Confirmed','Out for Delivery','Delivered','Cancelled') NOT NULL DEFAULT 'Pending',
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
 updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
 FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
 FOREIGN KEY (gas_id) REFERENCES gases(id) ON DELETE RESTRICT
);

CREATE TABLE IF NOT EXISTS enquiries (
 id INT AUTO_INCREMENT PRIMARY KEY,
 name VARCHAR(120) NOT NULL,
 email VARCHAR(160) NOT NULL,
 phone VARCHAR(20),
 message TEXT NOT NULL,
 created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO gases (gas_name,description,cylinder_size,available_quantity,status)
SELECT * FROM (
 SELECT 'Medical Oxygen','Reliable oxygen supply for healthcare requirements.','10L',25,'Available'
 UNION ALL SELECT 'Industrial Oxygen','Oxygen for welding, fabrication and industrial requirements.','10L',25,'Available'
 UNION ALL SELECT 'Nitrogen','Nitrogen gas for industrial and commercial applications.','10L',20,'Available'
 UNION ALL SELECT 'Argon','Argon gas for welding and industrial applications.','10L',20,'Available'
) AS seed
WHERE NOT EXISTS (SELECT 1 FROM gases);
