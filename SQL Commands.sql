CREATE DATABASE IF NOT EXISTS LibPro;
USE LibPro;

CREATE TABLE IF NOT EXISTS Inventory (
    SKUNumber VARCHAR(50) PRIMARY KEY,
    ISBN VARCHAR(13) NOT NULL CHECK (CHAR_LENGTH(ISBN) = 10 OR CHAR_LENGTH(ISBN) = 13),
    Status VARCHAR(100) NOT NULL CHECK (Status IN ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost')),
    BayNumber INT CHECK (BayNumber >= 0),
    ShelfNumber INT CHECK (ShelfNumber >= 0),
    RowNumber INT CHECK (RowNumber >= 0),
    ColumnNumber INT CHECK (ColumnNumber >= 0),
    AddedOn DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Books (
    BookNumber INT NOT NULL UNIQUE AUTO_INCREMENT,
    ISBN VARCHAR(13) PRIMARY KEY CHECK (CHAR_LENGTH(ISBN) = 10 OR CHAR_LENGTH(ISBN) = 13),
    Title VARCHAR(255) NOT NULL,
    Description TEXT,
    Author VARCHAR(100) NOT NULL,
    Publication VARCHAR(100) NOT NULL,
    Genre VARCHAR(100) NOT NULL,
    Language VARCHAR(50) NOT NULL,
    DateAdded DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastUpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Members (
    MemberNumber INT NOT NULL UNIQUE AUTO_INCREMENT,
    EmailID VARCHAR(255) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    MobileNumber CHAR(10) CHECK (MobileNumber BETWEEN '1000000000' AND '9999999999'),
    WishlistedBooks TEXT,
    Points INT DEFAULT 0 CHECK (Points >= 0),
    DateOfJoining DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastLoginOn DATETIME DEFAULT NULL,
    LastUpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Librarian (
    LibrarianNumber INT NOT NULL UNIQUE AUTO_INCREMENT,
    EmailID VARCHAR(255) PRIMARY KEY,
    FullName VARCHAR(100) NOT NULL,
    Password VARCHAR(255) NOT NULL,
    MobileNumber CHAR(10) UNIQUE CHECK (MobileNumber BETWEEN '1000000000' AND '9999999999'),
    DateOfJoining DATETIME DEFAULT CURRENT_TIMESTAMP,
    LastLoginOn DATETIME DEFAULT NULL,
    LastUpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS Reviews (
    ReviewID INT NOT NULL UNIQUE AUTO_INCREMENT,
    ISBN VARCHAR(13),
    ReviewerName VARCHAR(100) NOT NULL,
    ReviewerEmail VARCHAR(255) NOT NULL,
    Rating INT NOT NULL CHECK (Rating BETWEEN 1 AND 5),
    Review TEXT NOT NULL,
    ReviewedOn DATETIME DEFAULT CURRENT_TIMESTAMP,
    UpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS BooksRecord (
    RecordNumber INT NOT NULL AUTO_INCREMENT UNIQUE,
    SKU VARCHAR(50),
    Status ENUM('Borrowed', 'Returned', 'Lost') NOT NULL,
    ISBN VARCHAR(13) NOT NULL,
    Email VARCHAR(255),
    FullName VARCHAR(100),
    Points INT DEFAULT 0 CHECK (Points >= 0),
    DaysBorrowed INT DEFAULT 0 CHECK (DaysBorrowed >= 0),
    DaysLate INT DEFAULT 0 CHECK (DaysLate >= 0),
    Fine DECIMAL(10,2) DEFAULT 0.00 CHECK (Fine >= 0),
    DueOn DATE,
    ReturnedOn DATE,
    UpdatedOn DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    CreatedOn DATETIME DEFAULT CURRENT_TIMESTAMP
);

INSERT INTO Inventory (SKUNumber, ISBN, Status, BayNumber, ShelfNumber, RowNumber, ColumnNumber, AddedOn, UpdatedOn) VALUES
('SKU1001', '9780140449136', 'Shelved', 1, 1, 1, 1, '2025-01-10 10:15:00', '2025-06-25 00:13:16'),
('SKU1002', '0140449132', 'Borrowed', 0, 0, 0, 0, '2025-02-05 09:30:00', '2025-06-25 00:38:25'),
('SKU1003', '9780307269997', 'Damaged', 0, 0, 0, 0, '2025-03-12 16:20:00', '2025-06-25 00:38:57'),
('SKU1004', '9780679783268', 'Shelved', 3, 1, 1, 1, '2025-04-01 12:00:00', '2025-04-01 12:00:00'),
('SKU1005', '9780743273565', 'Unshelved', 0, 0, 0, 0, '2025-04-05 10:00:00', '2025-06-25 00:06:50'),
('SKU1006', '9780061120084', 'Shelved', 2, 3, 3, 3, '2025-04-10 11:00:00', '2025-04-10 11:00:00'),
('SKU1007', '9781982137274', 'Lost', 0, 0, 0, 0, '2025-04-15 11:30:00', '2025-06-25 00:39:44'),
('SKU1008', '9780345803481', 'Shelved', 3, 2, 1, 1, '2025-04-20 09:00:00', '2025-04-20 09:00:00'),
('SKU1009', '9780439023528', 'Unshelved', 0, 0, 0, 0, '2025-04-25 14:00:00', '2025-06-25 00:07:24'),
('SKU1010', '9780590353427', 'Shelved', 1, 3, 1, 4, '2025-04-30 15:00:00', '2025-04-30 15:00:00');

INSERT INTO Books (ISBN, Title, Description, Author, Publication, Genre, Language, DateAdded, LastUpdatedOn) VALUES
('9780140449136', 'Meditations', 'A series of personal writings by Marcus Aurelius', 'Marcus Aurelius', 'Penguin Classics', 'Philosophy', 'English', '2025-01-10 09:00:00', '2025-01-10 09:00:00'),
('0140449132', 'The Republic', 'Plato’s best-known work on justice and the ideal state', 'Plato', 'Oxford University Press', 'Philosophy', 'English', '2025-02-01 11:30:00', '2025-02-01 11:30:00'),
('9780307269997', 'The Girl with the Dragon Tattoo', 'A thriller novel by Stieg Larsson', 'Stieg Larsson', 'Vintage Crime/Black Lizard', 'Mystery', 'English', '2025-03-01 14:00:00', '2025-03-01 14:00:00'),
('9780679783268', 'Pride and Prejudice', 'A romantic novel by Jane Austen', 'Jane Austen', 'Modern Library', 'Fiction', 'English', '2025-04-01 10:00:00', '2025-04-01 10:00:00'),
('9780743273565', 'The Great Gatsby', 'A novel set in the Jazz Age by F. Scott Fitzgerald', 'F. Scott Fitzgerald', 'Scribner', 'Fiction', 'English', '2025-04-05 09:45:00', '2025-04-05 09:45:00'),
('9780061120084', 'To Kill a Mockingbird', 'A novel about racial injustice by Harper Lee', 'Harper Lee', 'Harper Perennial Modern Classics', 'Fiction', 'English', '2025-04-10 10:30:00', '2025-04-10 10:30:00'),
('9781982137274', 'Where the Crawdads Sing', 'A coming-of-age mystery novel', 'Delia Owens', 'G.P. Putnam\'s Sons', 'Mystery', 'English', '2025-04-15 11:00:00', '2025-04-15 11:00:00'),
('9780345803481', 'Fifty Shades of Grey', 'A romance novel by E. L. James', 'E. L. James', 'Vintage', 'Romance', 'English', '2025-04-20 08:15:00', '2025-04-20 08:15:00'),
('9780439023528', 'The Hunger Games', 'A dystopian novel by Suzanne Collins', 'Suzanne Collins', 'Scholastic Press', 'Dystopian', 'English', '2025-04-25 13:40:00', '2025-04-25 13:40:00'),
('9780590353427', 'Harry Potter and the Sorcerer\'s Stone', 'First book in the Harry Potter series', 'J.K. Rowling', 'Scholastic', 'Fantasy', 'English', '2025-04-30 14:30:00', '2025-04-30 14:30:00');

INSERT INTO Reviews (ReviewID, ISBN, ReviewerName, ReviewerEmail, Rating, Review, ReviewedOn, UpdatedOn) VALUES
(1, '0140449132', 'Thejas Rao', 'thejas@example.com', 5, 'Good Book!', '2025-06-24 23:05:24', '2025-06-24 23:05:24'),
(2, '0140449132', 'Thejas Rao', 'thejas@example.com', 4, 'This book was great, everything was so philosophical!', '2025-06-24 23:12:09', '2025-06-24 23:12:09'),
(3, '9781982137274', 'Thejas Rao', 'thejas@example.com', 5, 'Great Book!', '2025-06-24 23:20:21', '2025-06-24 23:20:21');

-- Default password for all seed accounts is '12345' (stored XOR-base64 encrypted as 'YUBSQF0=')
INSERT INTO Members (MemberNumber, EmailID, FullName, Password, MobileNumber, WishlistedBooks, Points, DateOfJoining, LastLoginOn, LastUpdatedOn) VALUES
(1, 'thoshit@example.com', 'Thoshit Gowda', 'YUBSQF0=', '9123456780', '9780140449136,9780679783268', 100, '2025-01-15 08:45:00', '2025-05-20 18:30:00', '2025-06-24 23:37:55'),
(2, 'thejas@example.com', 'Thejas Rao', 'YUBSQF0=', '9876543210', '0140449132', 55, '2025-02-10 10:00:00', '2025-06-25 00:55:12', '2025-06-25 00:55:11'),
(3, 'anita@example.com', 'Anita Sharma', 'YUBSQF0=', '9988776655', '', 30, '2025-03-12 11:30:00', '2025-05-01 14:30:00', '2025-05-01 14:30:00'),
(4, 'rajesh@example.com', 'Rajesh Iyer', 'YUBSQF0=', '9876512345', '9780307269997', 90, '2025-01-20 09:00:00', '2025-05-28 13:15:00', '2025-05-28 13:15:00'),
(5, 'divya@example.com', 'Divya Menon', 'YUBSQF0=', '9845123456', '', 60, '2025-02-14 08:20:00', '2025-06-01 16:00:00', '2025-06-01 16:00:00'),
(6, 'amit@example.com', 'Amit Rathi', 'YUBSQF0=', '9833445566', '9780679783268', 70, '2025-01-30 17:00:00', '2025-06-15 10:00:00', '2025-01-30 17:00:00'),
(7, 'sneha@example.com', 'Sneha Kulkarni', 'YUBSQF0=', '9798989898', '9780140449136', 40, '2025-03-25 10:10:00', '2025-06-10 09:45:00', '2025-06-10 09:45:00'),
(8, 'naveen@example.com', 'Naveen Joshi', 'YUBSQF0=', '9765432100', '', 20, '2025-01-05 12:30:00', '2025-06-15 10:00:00', '2025-01-05 12:30:00'),
(9, 'meera@example.com', 'Meera Das', 'YUBSQF0=', '9755551234', '0140449132,9780307269997', 95, '2025-02-22 15:00:00', '2025-06-15 10:00:00', '2025-06-24 22:59:37'),
(10, 'vikas@example.com', 'Vikas Bhat', 'YUBSQF0=', '9700011122', '', 55, '2025-03-10 13:45:00', '2025-05-31 08:00:00', '2025-05-31 08:00:00');

INSERT INTO Librarian (LibrarianNumber, EmailID, FullName, Password, MobileNumber, DateOfJoining, LastLoginOn, LastUpdatedOn) VALUES
(1, 'thejas.admin@example.com', 'Thejas Rao', 'YUBSQF0=', '9012345678', '2025-01-01 09:00:00', '2025-05-30 17:45:00', '2025-05-30 17:45:00'),
(2, 'thoshit.admin@example.com', 'Thoshit Gowda', 'YUBSQF0=', '9123456789', '2025-02-01 10:30:00', '2025-06-02 08:15:00', '2025-06-02 08:15:00');

INSERT INTO BooksRecord (RecordNumber, SKU, Status, ISBN, Email, FullName, Points, DaysBorrowed, DaysLate, Fine, DueOn, ReturnedOn, UpdatedOn, CreatedOn) VALUES
(1, 'SKU1002', 'Borrowed', '0140449132', 'thejas@example.com', 'Thejas Rao', 0, 14, 0, 0.00, '2025-07-01', NULL, '2025-06-24 22:57:58', '2025-06-17 10:00:00'),
(2, 'SKU1001', 'Returned', '9780140449136', 'sneha@example.com', 'Sneha Kulkarni', 10, 14, 0, 0.00, '2025-06-10', '2025-06-25', '2025-06-25 00:08:18', '2025-05-27 09:00:00'),
(3, 'SKU1007', 'Lost', '9781982137274', 'divya@example.com', 'Divya Menon', 0, 30, 0, 499.00, '2025-05-01', NULL, '2025-06-24 22:57:58', '2025-04-01 11:00:00'),
(4, 'SKU1005', 'Returned', '9780743273565', 'anita@example.com', 'Anita Sharma', 0, 14, 1, 2.00, '2025-04-20', '2025-06-24', '2025-06-24 23:03:52', '2025-04-06 08:45:00'),
(5, 'SKU1004', 'Returned', '9780679783268', 'amit@example.com', 'Amit Rathi', 10, 10, 0, 0.00, '2025-06-15', '2025-06-15', '2025-06-24 22:57:58', '2025-06-05 09:00:00'),
(6, 'SKU1009', 'Returned', '9780439023528', 'meera@example.com', 'Meera Das', 10, 10, 0, 0.00, '2025-06-28', '2025-06-24', '2025-06-24 22:59:37', '2025-06-18 14:00:00'),
(7, 'SKU1003', 'Returned', '9780307269997', 'rajesh@example.com', 'Rajesh Iyer', 5, 14, 2, 30.00, '2025-03-26', '2025-03-28', '2025-06-24 22:57:58', '2025-03-12 13:00:00'),
(8, 'SKU1006', 'Returned', '9780061120084', 'vikas@example.com', 'Vikas Bhat', 10, 15, 0, 0.00, '2025-06-15', '2025-06-15', '2025-06-24 22:57:58', '2025-06-01 10:30:00'),
(9, 'SKU1008', 'Returned', '9780345803481', 'naveen@example.com', 'Naveen Joshi', 5, 14, 1, 15.00, '2025-06-10', '2025-06-11', '2025-06-24 22:57:58', '2025-05-27 14:00:00'),
(10, 'SKU1010', 'Returned', '9780590353427', 'thoshit@example.com', 'Thoshit Gowda', 10, 7, 0, 0.00, '2025-06-20', '2025-06-20', '2025-06-24 22:57:58', '2025-06-13 09:30:00'),
(11, 'SKU1001', 'Returned', '9780140449136', 'thejas@example.com', 'Thejas Rao', 10, 10, 0, 0.00, '2025-06-20', '2025-06-25', '2025-06-25 00:08:18', '2025-06-10 09:00:00'),
(12, 'SKU1003', 'Returned', '9780307269997', 'thejas@example.com', 'Thejas Rao', 5, 14, 2, 30.00, '2025-05-15', '2025-05-17', '2025-06-24 22:57:58', '2025-05-01 12:00:00'),
(13, 'SKU1009', 'Returned', '9780439023528', 'thejas@example.com', 'Thejas Rao', 10, 3, 0, 0.00, '2025-06-23', '2025-06-24', '2025-06-24 22:59:37', '2025-06-20 08:30:00'),
(14, 'SKU1007', 'Lost', '9781982137274', 'thejas@example.com', 'Thejas Rao', 0, 15, 0, 499.00, '2025-04-30', NULL, '2025-06-24 22:57:58', '2025-04-15 11:00:00'),
(15, 'SKU1005', 'Returned', '9780743273565', 'thejas@example.com', 'Thejas Rao', 0, 14, 1, 2.00, '2025-03-20', '2025-06-24', '2025-06-24 23:03:52', '2025-03-06 14:00:00'),
(16, 'SKU1005', 'Returned', '0140449132', 'thejas@example.com', 'Thejas Rao', 0, 3, 1, 2.00, '2025-06-23', '2025-06-24', '2025-06-24 23:03:52', '2025-06-12 10:00:00'),
(17, 'SKU1001', 'Returned', '9780140449136', 'thejas@example.com', 'Thejas Rao', 10, 4, 0, 0.00, '2025-06-28', '2025-06-25', '2025-06-25 00:08:18', '2025-06-24 23:21:24');
