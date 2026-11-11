import ttkbootstrap as ttk
from tkinter import messagebox
from backend.bookrecord import get_record
from backend.books import get_book_det
from backend.reviews import add_review
from ui.common import make_scrollable_frame, make_book_card

def view_borrowed_books(app, email):
    def show_main_page():
        for w in app.winfo_children():
            w.destroy()

        records = get_record(email=email)
        if not records or not isinstance(records, list):
            records = []

        main = ttk.Frame(app, padding=20)
        main.pack(fill="both", expand=True)

        top_bar = ttk.Frame(main)
        top_bar.pack(fill="x", pady=(0, 15))

        ttk.Label(top_bar, text="📖 My Borrowed Books & Reading History", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")
        ttk.Label(top_bar, text=f"({len(records)} total records)", font=("Helvetica", 11), bootstyle="secondary").pack(side="left", padx=10, pady=(4, 0))

        panel = ttk.Frame(main)
        panel.pack(fill="both", expand=True)

        scrollable = make_scrollable_frame(panel)

        if records:
            valid_cards = 0
            for idx, rec in enumerate(records):
                sku = str(rec[1])
                rec_status = str(rec[2])
                isbn = str(rec[3])

                book_data = get_book_det(isbn=isbn)
                if not book_data or not isinstance(book_data, list):
                    continue
                book = book_data[0]

                rec_id = rec[0]

                card = make_book_card(
                    parent=scrollable,
                    book=book,
                    on_click=lambda current_rec_id=rec_id: show_details_page(current_rec_id),
                    status=rec_status
                )
                row, col = divmod(valid_cards, 4)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                valid_cards += 1

            for i in range(4):
                scrollable.grid_columnconfigure(i, weight=1)

            if valid_cards == 0:
                ttk.Label(scrollable, text="No borrowing history found 📭", font=("Helvetica", 13, "bold"), bootstyle="secondary").pack(pady=40)
        else:
            ttk.Label(scrollable, text="You have not borrowed any books yet 📭\nVisit the catalog to discover titles available at the library!", font=("Helvetica", 12), justify="center", bootstyle="secondary").pack(pady=40)

    def show_details_page(record_id):
        for w in app.winfo_children():
            w.destroy()

        all_records = get_record(email=email)
        rec = next((r for r in all_records if r[0] == record_id), None)
        if not rec:
            messagebox.showerror("Error", "Borrowing record not found.")
            show_main_page()
            return

        book_rows = get_book_det(isbn=rec[3])
        book_data = book_rows[0] if book_rows else None

        container = ttk.Frame(app, padding=20)
        container.pack(fill="both", expand=True)

        top_nav = ttk.Frame(container)
        top_nav.pack(fill="x", pady=(0, 15))

        ttk.Button(top_nav, text="⬅ Back to Borrowed Books", command=show_main_page, bootstyle="secondary-outline").pack(side="left")
        title_disp = book_data[2] if book_data else rec[1]
        sku = rec[1]
        ttk.Label(top_nav, text=f"📖 {title_disp} (SKU: {sku})", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left", padx=15)

        content = ttk.Frame(container)
        content.pack(fill="both", expand=True)

        info = ttk.Labelframe(content, text="Borrowing Details", padding=15, bootstyle="primary")
        info.pack(side="left", fill="both", expand=True, padx=(0, 10))

        try:
            fine_val = f"₹{float(rec[9]):.2f}" if rec[9] is not None else "₹0.00"
        except (ValueError, TypeError):
            fine_val = "₹0.00"
        returned_str = str(rec[11]) if rec[11] else "Not yet returned (Active)"
        borrowed_dt = str(rec[13])[:10] if (len(rec) > 13 and rec[13]) else "Unknown"

        fields = [
            ("SKU Number", rec[1]),
            ("Status", rec[2]),
            ("ISBN", rec[3]),
            ("Title", book_data[2] if book_data else "Unknown"),
            ("Author", book_data[4] if book_data else "Unknown"),
            ("Genre", book_data[6] if book_data else "Unknown"),
            ("Borrowed On", borrowed_dt),
            ("Days Allowed", rec[7]),
            ("Due Date", str(rec[10])),
            ("Returned On", returned_str),
            ("Days Late", rec[8] or 0),
            ("Late Fine", fine_val),
            ("ProPoints Awarded", rec[6] or 0)
        ]

        for label, value in fields:
            row = ttk.Frame(info, padding=3)
            row.pack(fill="x", pady=2)
            ttk.Label(row, text=f"{label}:", font=("Helvetica", 10, "bold"), bootstyle="secondary", width=18).pack(side="left")
            ttk.Label(row, text=str(value), font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

        right = ttk.Labelframe(content, text="Write a Review", padding=15, bootstyle="secondary")
        right.pack(side="right", fill="both", expand=True, padx=(10, 0))

        ttk.Label(right, text="Share your thoughts about this book:", font=("Helvetica", 10, "italic"), bootstyle="secondary").pack(anchor="w", pady=(0, 8))
        review_box = ttk.Text(right, height=6, wrap="word", font=("Helvetica", 10))
        review_box.pack(fill="x", pady=(0, 10))

        rating_row = ttk.Frame(right)
        rating_row.pack(fill="x", pady=(0, 10))
        ttk.Label(rating_row, text="Rating:", font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 8))
        rating_var = ttk.StringVar(value="5")
        ttk.Combobox(rating_row, textvariable=rating_var, values=["5 - Excellent", "4 - Good", "3 - Average", "2 - Fair", "1 - Poor"], width=15, state="readonly").pack(side="left")

        def submit_review():
            rev = review_box.get("1.0", "end").strip()
            if not rev:
                messagebox.showerror("Error", "Please enter your review text.")
                return

            rating_val = rating_var.get()[0]
            res = add_review(isbn=rec[3], fullname=rec[5], email=email, review=rev, rating=rating_val)
            if "successfully" in res.lower():
                messagebox.showinfo("Success", res)
                review_box.delete("1.0", "end")
                rating_var.set("5")
            else:
                messagebox.showerror("Error", res)

        ttk.Button(right, text="✅ Submit Review", command=submit_review, bootstyle="success").pack(anchor="w", pady=10)

    show_main_page()
