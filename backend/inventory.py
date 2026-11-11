from mysql.connector import Error
from backend.sql import execQy, fAll, fOne

def add_book_inv(sku, isbn, status, bay=0, shelf=0, row=0, column=0):
    try:
        sku = str(sku).strip()
        isbn = str(isbn).strip()
        if not sku or not isbn or not status:
            return "Error: SKU, ISBN, and Status are required."
        if status not in ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost'):
            return "Error: Invalid status."

        if len(isbn) == 9 and isbn.isdigit():
            isbn = isbn.zfill(10)
        elif len(isbn) == 12 and isbn.isdigit():
            isbn = isbn.zfill(13)

        if not isbn.isdigit() or len(isbn) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."

        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return f"Error: Book with ISBN '{isbn}' does not exist in the catalog. Please add book details in Manage Books first."

        try:
            bay = int(bay) if bay is not None and str(bay).strip() != "" else 0
            shelf = int(shelf) if shelf is not None and str(shelf).strip() != "" else 0
            row = int(row) if row is not None and str(row).strip() != "" else 0
            column = int(column) if column is not None and str(column).strip() != "" else 0
        except ValueError:
            return "Error: Bay, shelf, row, and column numbers must be integers."

        if fOne("SELECT 1 FROM Inventory WHERE SKUNumber = %s", (sku,)):
            return "Error: SKU number already exists."

        ok = execQy("""
            INSERT INTO Inventory 
            (SKUNumber, ISBN, Status, BayNumber, ShelfNumber, RowNumber, ColumnNumber)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (sku, isbn, status, bay, shelf, row, column))
        if not ok:
            return "Error: Failed to add inventory item to database."
        return "Inventory item added successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def update_book_inv(sku, status=None, bay=None, shelf=None, row=None, column=None, eraseBInfo=False):
    try:
        sku = str(sku).strip() if sku else ""
        if not sku:
            return "Error: SKU is required."
        if not fOne("SELECT 1 FROM Inventory WHERE SKUNumber = %s", (sku,)):
            return "Error: SKU not found in inventory."

        if eraseBInfo:
            execQy("UPDATE Inventory SET BayNumber = 0, ShelfNumber = 0, RowNumber = 0, ColumnNumber = 0 WHERE SKUNumber = %s", (sku,))

        updates, values = [], []
        if status:
            if status not in ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost'):
                return "Error: Invalid status."
            updates.append("Status = %s")
            values.append(status)

        for field, val in [("BayNumber", bay), ("ShelfNumber", shelf),
                           ("RowNumber", row), ("ColumnNumber", column)]:
            if val is not None and str(val).strip() != "":
                try:
                    num_val = int(val)
                    updates.append(f"{field} = %s")
                    values.append(num_val)
                except ValueError:
                    return f"Error: {field} must be an integer."

        if not updates:
            if eraseBInfo:
                return "Inventory record updated successfully."
            return "Error: No fields provided to update."

        values.append(sku)
        ok = execQy(f"UPDATE Inventory SET {', '.join(updates)} WHERE SKUNumber = %s", tuple(values))
        if not ok:
            return "Error: Failed to update inventory record."
        return "Inventory record updated successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_book_inv(isbn=None, sku=None, status=None, count=False):
    try:
        if status and status not in ('Shelved', 'Unshelved', 'Missing', 'Damaged', 'Borrowed', 'Lost'):
            return 0 if count else []

        sel = "COUNT(*)" if count else "*"
        query = f"SELECT {sel} FROM Inventory"
        conditions, values = [], []

        if isbn:
            val = str(isbn).strip()
            if len(val) == 9 and val.isdigit():
                val = val.zfill(10)
            elif len(val) == 12 and val.isdigit():
                val = val.zfill(13)
            if not val.isdigit() or len(val) not in (10, 13):
                return 0 if count else []
            conditions.append("ISBN = %s")
            values.append(val)

        if sku:
            conditions.append("SKUNumber = %s")
            values.append(str(sku).strip())

        if status:
            conditions.append("Status = %s")
            values.append(status)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        if count:
            row = fOne(query, tuple(values))
            return row[0] if row else 0

        rows = fAll(query, tuple(values))
        return rows if rows is not None else []
    except Exception:
        return 0 if count else []

def delete_book_inv(sku=None, isbn=None, row=None, column=None, shelf=None, bay=None):
    try:
        conditions, values = [], []
        for field, val in [("SKUNumber", sku), ("ISBN", isbn), ("RowNumber", row),
                           ("ColumnNumber", column), ("ShelfNumber", shelf), ("BayNumber", bay)]:
            if val is not None and str(val).strip() != "":
                conditions.append(f"{field} = %s")
                values.append(str(val).strip())

        if not conditions:
            return "Error: At least one condition is required to delete inventory items."

        where_clause = " AND ".join(conditions)
        if not fOne(f"SELECT 1 FROM Inventory WHERE {where_clause}", tuple(values)):
            return "Error: No matching inventory items found."

        ok = execQy(f"DELETE FROM Inventory WHERE {where_clause}", tuple(values))
        if not ok:
            return "Error: Failed to delete inventory record."
        return "Inventory item(s) deleted successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"
