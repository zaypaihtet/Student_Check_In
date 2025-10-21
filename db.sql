CREATE DATABASE IF NOT EXISTS attendance_system;
USE attendance_system;

CREATE TABLE admin (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100),
    password VARCHAR(255)
);

INSERT INTO admin (username, password)
VALUES ('admin', 'admin123');

CREATE TABLE batches (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_name VARCHAR(100)
);

CREATE TABLE attendance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    student_name VARCHAR(100),
    batch_id INT,
    ip_address VARCHAR(50),
    location VARCHAR(100),
    status VARCHAR(20) DEFAULT 'Present',
    checkin_time DATETIME DEFAULT CURRENT_TIMESTAMP,
    date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);

CREATE TABLE topics (
    id INT AUTO_INCREMENT PRIMARY KEY,
    batch_id INT,
    teacher_name VARCHAR(100),
    topic VARCHAR(255),
    date DATE DEFAULT (CURRENT_DATE),
    FOREIGN KEY (batch_id) REFERENCES batches(id)
);
