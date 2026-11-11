from mysql.connector import Error
from backend.sql import execQy, fAll, fOne

def add_review(isbn, fullname, email, review, rating):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        fullname_str = str(fullname).strip() if fullname else ""
        email_str = str(email).strip() if email else ""
        review_str = str(review).strip() if review else ""
        rating_str = str(rating).strip() if rating is not None else ""

        if not all([isbn_str, fullname_str, email_str, review_str, rating_str]):
            return "Error: All fields are required."
        if not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if not rating_str.isdigit() or not (1 <= int(rating_str) <= 5):
            return "Error: Rating must be an integer between 1 and 5."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: Book not found."

        ok = execQy("""
            INSERT INTO Reviews (ISBN, ReviewerName, ReviewerEmail, Rating, Review)
            VALUES (%s, %s, %s, %s, %s)
        """, (isbn_str, fullname_str, email_str, int(rating_str), review_str))
        if not ok:
            return "Error: Failed to save review."
        return "Review added successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def update_review(isbn, email, review, rating):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        email_str = str(email).strip() if email else ""
        review_str = str(review).strip() if review else ""
        rating_str = str(rating).strip() if rating is not None else ""

        if not all([isbn_str, email_str, review_str, rating_str]):
            return "Error: All fields are required."
        if not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if not rating_str.isdigit() or not (1 <= int(rating_str) <= 5):
            return "Error: Rating must be an integer between 1 and 5."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: Book not found."

        ok = execQy("""
            UPDATE Reviews SET Review = %s, Rating = %s
            WHERE ISBN = %s AND ReviewerEmail = %s
        """, (review_str, int(rating_str), isbn_str, email_str))
        if not ok:
            return "Error: Failed to update review."
        return "Review updated successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def delete_review(isbn, email):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        email_str = str(email).strip() if email else ""
        if not isbn_str or not email_str:
            return "Error: ISBN and email are required."
        if not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return "Error: Invalid ISBN. Must be 10 or 13 digits."
        if not fOne("SELECT 1 FROM Books WHERE ISBN = %s", (isbn_str,)):
            return "Error: Book not found."

        ok = execQy("DELETE FROM Reviews WHERE ISBN = %s AND ReviewerEmail = %s", (isbn_str, email_str))
        if not ok:
            return "Error: Failed to delete review."
        return "Review deleted successfully."
    except Error as e:
        return f"Database Error: {e}"
    except Exception as e:
        return f"Error: {e}"

def get_reviews(isbn):
    try:
        isbn_str = str(isbn).strip() if isbn else ""
        if len(isbn_str) == 9 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(10)
        elif len(isbn_str) == 12 and isbn_str.isdigit():
            isbn_str = isbn_str.zfill(13)

        if not isbn_str or not isbn_str.isdigit() or len(isbn_str) not in (10, 13):
            return []

        reviews = fAll("SELECT * FROM Reviews WHERE ISBN = %s ORDER BY ReviewID DESC", (isbn_str,))
        return reviews if reviews is not None else []
    except Exception:
        return []
