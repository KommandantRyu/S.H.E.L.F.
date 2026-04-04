-- Use after older database versions that stored credentials as password_hash
-- and kept an extra column on `users` (drop that column if it exists in your schema).
USE library_db;

ALTER TABLE users
  CHANGE COLUMN `password_hash` `password` VARCHAR(255) NOT NULL;

ALTER TABLE users
  DROP COLUMN `role`;
