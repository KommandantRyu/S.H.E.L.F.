-- Run once against library_db from the original class dumps
-- (users had name + password; purchases in bought_books).
USE library_db;

ALTER TABLE books
  MODIFY COLUMN price DECIMAL(10,2) NOT NULL DEFAULT 0.00;

ALTER TABLE users
  CHANGE COLUMN `name` `username` VARCHAR(255) NOT NULL;

ALTER TABLE users
  ADD COLUMN `created_at` TIMESTAMP NULL DEFAULT CURRENT_TIMESTAMP;

RENAME TABLE bought_books TO purchased_books;
