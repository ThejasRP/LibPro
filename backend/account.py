from datetime import datetime
from mysql.connector import Error
from backend.sql import execQy, fOne, fAll
from backend.constants import LIBRARIAN_HEADERS, MEMBER_HEADERS
from backend.utils import encrypt_password, decrypt_password, validate_fields

HEADERS_MAP = {
    "Librarian": LIBRARIAN_HEADERS,
    "Members": MEMBER_HEADERS,
}

def _validate_user_type(db): 
    if db not in HEADERS_MAP:
        raise ValueError("Error: Invalid user type.")

def _validate_mobile(mobile):
    m = str(mobile).strip() if mobile is not None else ""
    if not (m.isdigit() and len(m) == 10 and m[0] in "123456789"):
        raise ValueError("Error: Invalid mobile number. Must be a 10-digit number starting with 1-9.")

def _ensure_email_exists(db, email):
    row = fOne(f"SELECT Password FROM {db} WHERE EmailID = %s", (email,))
    if not row:
        raise ValueError("Error: Email not found.")
    return decrypt_password(row[0])

def _ensure_member_exists(email):
    row = fOne("SELECT Points FROM Members WHERE EmailID = %s", (email,))
    if not row:
        raise ValueError("Error: Member not found.")
    return row[0]

def signup_user(db, email, fullname, password, mobile):
    try:
        _validate_user_type(db)
        email = str(email).strip() if email else ""
        fullname = str(fullname).strip() if fullname else ""
        password = str(password).strip() if password else ""
        mobile = str(mobile).strip() if mobile else ""
        if not all([email, fullname, password, mobile]):
            return "Error: All fields are required."
        _validate_mobile(mobile)
        if fOne(f"SELECT 1 FROM {db} WHERE EmailID = %s", (email,)):
            return "Error: Email already registered."

        ok = execQy(
            f"INSERT INTO {db} (EmailID, FullName, Password, MobileNumber) VALUES (%s, %s, %s, %s)",
            (email, fullname, encrypt_password(password), mobile),
        )
        if not ok:
            return "Error: Failed to register user."
        return "Signup successful."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def signin_user(db, email, password):
    try:
        _validate_user_type(db)
        if not email or not password:
            return "Error: Email and password are required."

        stored_pwd = _ensure_email_exists(db, email)
        if password != stored_pwd:
            return "Error: Invalid email or password."

        execQy(f"UPDATE {db} SET LastLoginOn = %s WHERE EmailID = %s", (datetime.now(), email))
        return "Login successful."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def update_user(db, email, old_password=None, fullname=None, mobile=None, new_password=None, is_admin=False):
    try:
        _validate_user_type(db)
        if not email:
            return "Error: Email is required."

        if not is_admin:
            if not old_password:
                return "Error: Current password is required."
            if old_password != _ensure_email_exists(db, email):
                return "Error: Current password is incorrect."

        fields, values = [], []
        if fullname: 
            fields.append("FullName = %s")
            values.append(fullname)
        if mobile:
            _validate_mobile(mobile)
            fields.append("MobileNumber = %s")
            values.append(mobile)
        if new_password: 
            fields.append("Password = %s")
            values.append(encrypt_password(new_password))

        if not fields:
            return "Error: Nothing to update."

        values.append(email)
        ok = execQy(f"UPDATE {db} SET {', '.join(fields)} WHERE EmailID = %s", tuple(values))
        if not ok:
            return "Error: Update failed in database."
        return "Update successful."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def delete_user(db, email, password, librarianEmail=None):
    try:
        _validate_user_type(db)
        if not email or not password:
            return "Error: Email and password are required."

        verify_email = librarianEmail if librarianEmail else email
        verify_db = "Librarian" if librarianEmail else db
        admin_pwd = _ensure_email_exists(verify_db, verify_email)
        if admin_pwd != password:
            return "Error: Incorrect password."

        if db == "Members":
            if fOne("SELECT 1 FROM BooksRecord WHERE Email = %s AND Status = 'Borrowed'", (email,)):
                return "Error: Cannot delete member account with active borrowed books. Please return all books first."

        ok = execQy(f"DELETE FROM {db} WHERE EmailID = %s", (email,))
        if not ok:
            return "Error: Failed to delete user."
        return "Account deleted successfully."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def get_user(db, fields=None, email=None, count=False, bool=False):
    try:
        _validate_user_type(db)
        selected_fields = validate_fields(fields, HEADERS_MAP[db]) if fields else "*"
        if selected_fields == "INVALID":
            return None if not bool else False

        if email:
            row = fOne(f"SELECT {selected_fields} FROM {db} WHERE EmailID = %s", (email,))
            if bool:
                return row is not None
            return row

        if count:
            row = fOne(f"SELECT COUNT(*) FROM {db}")
            return row[0] if row else 0

        rows = fAll(f"SELECT {selected_fields} FROM {db}")
        return rows if rows is not None else []
    except (ValueError, Error):
        return False if bool else None
    except Exception:
        return False if bool else None

def wishlist_mem(email, isbn, action):
    try:
        if not all([email, isbn, action]):
            return "Error: Email, ISBN, and action are required."
        isbn_str = str(isbn).strip()
        if not (isbn_str.isdigit() and len(isbn_str) in (10, 13)):
            return "Error: Invalid ISBN."
        if action not in ("added", "removed"):
            return "Error: Action must be 'added' or 'removed'."

        row = fOne("SELECT WishlistedBooks FROM Members WHERE EmailID = %s", (email,))
        if not row:
            return "Error: Member not found."

        wishlist = [b.strip() for b in row[0].split(",") if b.strip()] if row[0] else []

        if action == "added":
            if isbn_str in wishlist: 
                return "Error: ISBN already in wishlist."
            wishlist.append(isbn_str)
        else:
            if isbn_str not in wishlist: 
                return "Error: ISBN not in wishlist."
            wishlist.remove(isbn_str)

        ok = execQy("UPDATE Members SET WishlistedBooks = %s WHERE EmailID = %s", (",".join(wishlist), email))
        if not ok:
            return "Error: Could not update wishlist."
        return f"{action.title()} book in wishlist."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def add_points_mem(email, isbn, val=10):
    try:
        if not email or not isbn:
            return "Error: Email and ISBN are required."

        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn,)):
            return "Error: Book not found."

        current_points = _ensure_member_exists(email)
        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (current_points + val, email))
        return val
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"

def redeem_points_mem(email, points):
    try:
        if not email or points is None:
            return "Error: Email and points are required."
        if not str(points).isdigit() or int(points) <= 0:
            return "Error: Invalid points."

        points = int(points)
        current_points = _ensure_member_exists(email)
        if current_points < points:
            return "Error: Insufficient points."

        execQy("UPDATE Members SET Points = %s WHERE EmailID = %s", (current_points - points, email))
        return f"{points} points redeemed. New total: {current_points - points}."
    except (ValueError, Error) as e:
        return str(e)
    except Exception as e:
        return f"Error: {e}"
