from mysql.connector import Error
from datetime import datetime, timedelta
from backend.account import add_points_mem
from backend.inventory import update_book_inv
from backend.sql import execQy, fAll, fOne

def borrow_book(email, sku, fullname, isbn, daysborrowed):
    try:
        if not all([email, sku, fullname, isbn, daysborrowed]):
            return "Error: All fields are required."

        email = str(email).strip()
        sku = str(sku).strip()
        fullname = str(fullname).strip()
        isbn = str(isbn).strip()
        days_str = str(daysborrowed).strip()

        if not days_str.isdigit() or int(days_str) <= 0:
            return "Error: Days borrowed must be a positive integer."
        days = int(days_str)

        if fOne("SELECT 1 FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'", (sku,)):
            return "Error: This book is already borrowed and not yet returned."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return "Error: Invalid ISBN: Book not found."

        inv_item = fOne("SELECT Status FROM Inventory WHERE SKUNumber = %s", (sku,))
        if not inv_item:
            return "Error: SKU not found in inventory."
        if inv_item[0] == "Borrowed":
            return "Error: This book copy is currently marked as borrowed."
        if inv_item[0] in ("Lost", "Damaged", "Missing"):
            return f"Error: Cannot borrow book copy because inventory status is '{inv_item[0]}'."

        due_on = (datetime.now() + timedelta(days=days)).date()
        ok = execQy("""
            INSERT INTO BooksRecord 
            (SKU, Status, ISBN, Email, FullName, DaysBorrowed, DueOn)
            VALUES (%s, 'Borrowed', %s, %s, %s, %s, %s)
        """, (sku, isbn, email, fullname, days, due_on))
        if not ok:
            return "Error: Failed to record borrowing transaction."

        update_book_inv(sku, status="Borrowed", eraseBInfo=True)
        return "Book borrowed successfully."
    except Exception as e:
        return f"Error: {e}"

def return_book(sku):
    try:
        sku = str(sku).strip() if sku else ""
        if not sku:
            return "Error: SKU is required."

        record = fOne("SELECT Status, DueOn, Email, ISBN FROM BooksRecord WHERE SKU = %s AND Status = 'Borrowed'", (sku,))
        if not record:
            return "Error: Active borrowed book record not found for this SKU."

        status, due_on, email, isbn = record
        today = datetime.now().date()
        days_late = max((today - due_on).days, 0)
        fine = round(days_late * 2.0, 2)
        awarded_pts = add_points_mem(email, isbn, 10) if days_late == 0 else 0
        points = awarded_pts if isinstance(awarded_pts, int) else 0

        ok = execQy("""
            UPDATE BooksRecord
            SET Status = 'Returned', ReturnedOn = %s, DaysLate = %s, Fine = %s, Points = %s
            WHERE SKU = %s AND Status = 'Borrowed'
        """, (today, days_late, fine, points, sku))
        if not ok:
            return "Error: Failed to update return record."

        update_book_inv(sku, status="Unshelved", eraseBInfo=True)
        return f"Book returned successfully.\n\nFine to be paid: ₹{fine:.2f}/-\nPoints awarded: {points}."
    except Exception as e:
        return f"Database Error: {e}"

def get_record(sku=None, status=None, email=None, count=False):
    try:
        fields = "COUNT(*)" if count else "*"
        conditions, values = [], []

        if sku:
            conditions.append("SKU = %s")
            values.append(str(sku).strip())
        if email:
            conditions.append("Email = %s")
            values.append(str(email).strip())
        if status:
            if status not in ("Borrowed", "Returned", "Lost"):
                return 0 if count else []
            conditions.append("Status = %s")
            values.append(status)

        query = f"SELECT {fields} FROM BooksRecord"
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        query += " ORDER BY RecordNumber DESC"

        if count:
            result = fOne(query, tuple(values))
            return result[0] if result else 0

        if sku and not status and not email:
            result = fOne(query, tuple(values))
            if not result:
                return None
            keys = [
                "RecordNumber", "SKU", "Status", "ISBN", "Email", "FullName",
                "Points", "DaysBorrowed", "DaysLate", "Fine", "DueOn",
                "ReturnedOn", "UpdatedOn", "CreatedOn"
            ]
            record = dict(zip(keys, result))
            fine_val = record.get("Fine")
            try:
                record["Fine"] = f"₹{float(fine_val):.2f}/-" if fine_val is not None else "₹0.00/-"
            except (ValueError, TypeError):
                record["Fine"] = "₹0.00/-"
            record["Points"] = record.get("Points") or 0
            record["ReturnedOn"] = str(record["ReturnedOn"]) if record.get("ReturnedOn") else "Not yet returned"
            record["DueOn"] = str(record["DueOn"]) if record.get("DueOn") else ""
            record["DaysLate"] = record.get("DaysLate") or 0
            return record

        rows = fAll(query, tuple(values))
        return rows if rows is not None else []
    except Exception:
        return 0 if count else []

def overdue_books(sku=None, email=None, count=False):
    try:
        today = datetime.now().date()
        conditions, values = ["Status = 'Borrowed'", "DueOn < %s"], [today]

        if sku:
            conditions.append("SKU = %s")
            values.append(str(sku).strip())
        if email:
            conditions.append("Email = %s")
            values.append(str(email).strip())

        where_clause = " AND ".join(conditions)

        if count:
            result = fOne(f"SELECT COUNT(*) FROM BooksRecord WHERE {where_clause}", tuple(values))
            return result[0] if result else 0

        query = f"""
            SELECT SKU, FullName, DATEDIFF(CURDATE(), DueOn) AS DaysLate, DueOn, ROUND(DATEDIFF(CURDATE(), DueOn) * 2.0, 2) AS Fine
            FROM BooksRecord
            WHERE {where_clause}
            ORDER BY DueOn ASC
        """
        records = fAll(query, tuple(values))
        return records if records is not None else []
    except Exception:
        return 0 if count else []
