# LibPro

A modern desktop Library Management System (LMS) built with Python, Tkinter (ttkbootstrap), and MySQL, featuring role-based access control, barcode/ISBN scanning, inventory bay tracking, and member loyalty rewards.

## Features

- **Role-based Authentication**: Separate specialized portals for Librarians (Admins) and Members.
- **Catalog Management**: Add, update, search, filter by genre, and delete books with automatic ISBN validation.
- **Physical Bay & Shelf Tracking**: Map copies to specific bays, shelves, rows, and columns for rapid physical shelf retrieval.
- **Circulation & Due Date Engine**: Issue and return books with automated fine calculations and on-time return points.
- **Barcode & ISBN Scanner**: Supports live webcam scanning, barcode image upload, and handheld USB laser barcode guns.
- **Member Wishlist & Reviews**: Members can save books to their personal reading list and leave community ratings and reviews.
- **ProPoints Loyalty Program**: Members earn points for returning books on time and can redeem them for library perks and merchandise.
- **Interactive Dashboards**: Real-time stats on borrowed books, overdue accounts, bay inventory, and active transactions.

## Tech stack

- **Python 3.10+**
- **Tkinter + ttkbootstrap** (Modern dark UI theme)
- **MySQL 8.0+** (Relational database storage)
- **OpenCV & zxing-cpp** (Computer vision barcode and ISBN decoding)
- **Pillow (PIL)** (Image handling and UI asset rendering)

## Getting started

### Prerequisites
- Python 3.10 or higher installed. Ensure `Add Python to PATH` is checked during installation.
- MySQL Server 8.0+ running locally (or via MySQL Workbench / XAMPP / Docker).

### 1. Clone or download the repository:
```bash
git clone https://github.com/ThejasRP/libpro.git
cd libpro
```

### 2. Install dependencies:
```bash
pip install -r requirements.txt
```

### 3. Set up the MySQL database:
1. Open your MySQL client (MySQL Workbench, phpMyAdmin, or MySQL CLI).
2. Execute the included script `SQL Commands.sql`:
   ```bash
   mysql -u root -p < "SQL Commands.sql"
   ```
   This creates the `LibPro` database schema and pre-populates safe RFC 2606 sample books, inventory copies, member accounts, and librarian logins.

### 4. Configure database credentials:
Edit `db_config.json` in the root folder with your MySQL credentials:
```json
{
  "host": "localhost",
  "port": 3306,
  "user": "root",
  "password": "your_mysql_password",
  "database": "LibPro"
}
```
*(Alternatively, set the environment variables `DB_HOST`, `DB_PORT`, `DB_USER`, and `DB_PASS`.)*

### 5. Launch the application:
```bash
python app.py
```

## First-time setup

When logging in for the first time, you can use the pre-seeded demo accounts (all seed passwords are set to `12345`):

### Librarian (Admin) Portal
- **Email**: `thejas.admin@example.com` *(or `thoshit.admin@example.com`)*
- **Password**: `12345`
- **Role selector**: Select **Librarian**

### Member Portal
- **Email**: `thejas@example.com` *(or `thoshit@example.com`, `amit@example.com`)*
- **Password**: `12345`
- **Role selector**: Select **Member**

> **Tip**: All mock records use RFC 2606 reserved example domains (`@example.com`) that can never exist or resolve to real internet addresses, protecting personal privacy. New members can also be registered directly through the Member Manager inside the Librarian dashboard.


## Authors & Project Context

This project was developed collaboratively as the **Class 12 CBSE Computer Science Practical Capstone Project**:

| Contributor | GitHub Profile | Role |
| :--- | :--- | :--- |
| **Thejas** | [@ThejasRP](https://github.com/ThejasRP) | Co-Creator & Developer |
| **Thoshit Gowda** | [@Thoshit-Gowda](https://github.com/Thoshit-Gowda) | Co-Creator & Developer |

## Notes
- AI was used for generating this README, UI and feature enhancements.
- Barcode scanning works with live webcams, sample images (`ui/images/sample_isbn.png`, `ui/images/sample_sku.png`), and standard plug-and-play USB barcode scanners.
- Due dates and overdue late fines (₹2.00/day) are automatically computed upon book check-in.
- On-time book returns automatically grant ProPoints to member accounts.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.
