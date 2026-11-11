from mysql.connector import Error
from backend.sql import execQy, fAll, fOne
from backend.inventory import delete_book_inv

def add_book_det(isbn, title, author, publication, genre, language, description=None):
    try:
        if not all([isbn, title, author, publication, genre, language]):
            return "Error: All fields except description are required."
        isbn_str = str(isbn).strip()
        if not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: This book already exists."

        ok = execQy("""
            INSERT INTO Books (ISBN, Title, Description, Author, Publication, Genre, Language)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (isbn_str, title.strip(), description.strip() if description else "", author.strip(), publication.strip(), genre.strip(), language.strip()))
        if not ok:
            return "Error: Failed to insert book into database."
        return "Book added successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def update_book_det(isbn, title=None, description=None, author=None, publication=None, genre=None, language=None):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        if not isbn_str or not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: Book not found."

        fields, values = [], []
        for col, val in [("Title", title), ("Description", description), ("Author", author),
                         ("Publication", publication), ("Genre", genre), ("Language", language)]:
            if val is not None and (str(val).strip() != "" or col == "Description"):
                fields.append(f"{col} = %s")
                values.append(str(val).strip())

        if not fields:
            return "Error: Nothing to update."

        values.append(isbn_str)
        ok = execQy(f"UPDATE Books SET {', '.join(fields)} WHERE ISBN = %s", tuple(values))
        if not ok:
            return "Error: Failed to update book in database."
        return "Book updated successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def delete_book_det(isbn):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        if not isbn_str or not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: Book not found."

        delete_book_inv(isbn=isbn_str)
        ok = execQy("DELETE FROM Books WHERE ISBN = %s", (isbn_str,))
        if not ok:
            return "Error: Failed to delete book from database."
        return "Book deleted successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_book_det(isbn=None, title=None, author=None, publication=None, genre=None, language=None):
    try:
        if not any([isbn, title, author, publication, genre, language]):
            rows = fAll("SELECT * FROM Books ORDER BY BookNumber DESC")
            return rows if rows is not None else []

        isbn_str = str(isbn).strip() if isbn else None
        if isbn_str:
            if len(isbn_str) == 9 and isbn_str.isdigit():
                isbn_str = isbn_str.zfill(10)
            elif len(isbn_str) == 12 and isbn_str.isdigit():
                isbn_str = isbn_str.zfill(13)
            if not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
                return []

        conditions, values = [], []
        for col, val in [("ISBN", isbn_str), ("Title", title), ("Author", author),
                         ("Publication", publication), ("Genre", genre), ("Language", language)]:
            if val:
                op = "LIKE" if col != "ISBN" else "="
                v = f"%{val.strip()}%" if op == "LIKE" else val.strip()
                conditions.append(f"{col} {op} %s")
                values.append(v)

        query = "SELECT * FROM Books WHERE " + " AND ".join(conditions) + " ORDER BY BookNumber DESC"
        rows = fAll(query, tuple(values))
        return rows if rows is not None else []
    except Exception:
        return []

def get_books_list(isbns):
    try:
        cleaned_isbns = [str(i).strip() for i in isbns if str(i).strip().isdigit() and len(str(i).strip()) in (10, 13)]
        if not cleaned_isbns:
            return []

        placeholders = ','.join(['%s'] * len(cleaned_isbns))
        query = f"SELECT * FROM Books WHERE ISBN IN ({placeholders}) ORDER BY BookNumber DESC"
        rows = fAll(query, tuple(cleaned_isbns))
        return rows if rows is not None else []
    except Exception:
        return []
