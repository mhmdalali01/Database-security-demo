CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  password_hash VARBINARY(255),
  password_encrypted VARBINARY(255),
  storage_method ENUM('hash','encrypt') NOT NULL,
  UNIQUE KEY username (username)
);