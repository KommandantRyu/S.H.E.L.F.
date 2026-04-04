-- Run once against an existing library_db created from the older dump files
-- (users had name/password; purchases lived in bought_books).
USE library_db;

-- Books: allow inserts without an explicit price
ALTER TABLE books
  MODIFY COLUMN price DECIMAL(10,2) NOT NULL DEFAULT 0.00;

-- Users: column names and fields expected by the Flask app
ALTER TABLE users
  CHANGE COLUMN `name` `username` VARCHAR(255) NOT NULL,
  CHANGE COLUMN `password` `password_hash` VARCHAR(255) NOT NULL;

ALTER TABLE users
  ADD COLUMN `role` VARCHAR(20) NOT NULL DEFAULT 'user' AFTER `password_hash`,
  ADD COLUMN `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP;

-- Purchases table name used in application code
RENAME TABLE bought_books TO purchased_books;
