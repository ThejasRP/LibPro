import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from backend.inventory import get_book_inv
from backend.reviews import get_reviews, add_review
from backend.books import get_book_det
from backend.account import get_user, wishlist_mem
from ui.common import _bind_mousewheel

def add_to_wishlist(email, isbn):
    res = wishlist_mem(email, isbn, "added")
    if "added" in res.lower():
        messagebox.showinfo("Wishlist", res)
    else:
        messagebox.showerror("Wishlist", res)

def remove_from_wishlist(app, email, isbn, revert):
    res = wishlist_mem(email, isbn, "removed")
    if "removed" in res.lower():
        messagebox.showinfo("Wishlist", res)
        for widget in app.winfo_children():
            widget.destroy()
        revert()
    else:
        messagebox.showerror("Wishlist", res)

def show_details_page(app, email, revert, isbn, write_reviews=True, wishlist_mode="added"):
    for widget in app.winfo_children():
        widget.destroy()

    books_matched = get_book_det(isbn=isbn)
    if not books_matched or not isinstance(books_matched, list):
        messagebox.showerror("Error", f"Book with ISBN '{isbn}' not found.")
        revert()
        return

    book = books_matched[0]

    main_frame = ttk.Frame(app, padding=20)
    main_frame.pack(fill="both", expand=True)

    top_nav = ttk.Frame(main_frame)
    top_nav.pack(fill="x", pady=(0, 15))

    ttk.Button(top_nav, text="⬅ Back", command=revert, bootstyle="secondary-outline").pack(side="left")
    ttk.Label(top_nav, text=f"📘 {book[2]}", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left", padx=15)

    content = ttk.Frame(main_frame)
    content.pack(fill="both", expand=True)

    left_panel = ttk.Labelframe(content, text="Book Information", padding=15, bootstyle="primary")
    left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))

    canvas = ttk.Canvas(left_panel, highlightthickness=0)
    scroll_y = ttk.Scrollbar(left_panel, orient="vertical", command=canvas.yview, bootstyle="round")
    scrollable = ttk.Frame(canvas)

    win_id = canvas.create_window((0, 0), window=scrollable, anchor="nw")
    canvas.configure(yscrollcommand=scroll_y.set)

    def on_c_cfg(e):
        canvas.itemconfig(win_id, width=e.width)

    def on_f_cfg(e):
        canvas.configure(scrollregion=canvas.bbox("all"))

    canvas.bind("<Configure>", on_c_cfg)
    scrollable.bind("<Configure>", on_f_cfg)

    canvas.pack(side="left", fill="both", expand=True)
    scroll_y.pack(side="right", fill="y")
    _bind_mousewheel(scrollable, canvas)

    available_qty = get_book_inv(isbn=isbn, status="Shelved", count=True)
    total_qty = get_book_inv(isbn=isbn, count=True)

    stock_text = f"{available_qty} copy available" if available_qty == 1 else f"{available_qty} copies available"
    if total_qty > 0:
        stock_text += f" ({total_qty} total copies in library)"
    else:
        stock_text = "Out of circulation"

    fields = [
        ("Title", book[2]),
        ("Author", book[4]),
        ("Genre", book[6]),
        ("Publisher", book[5]),
        ("Language", book[7]),
        ("ISBN", book[1]),
        ("Availability", stock_text),
        ("Description", book[3] or "No synopsis available."),
    ]

    for key, val in fields:
        f = ttk.Frame(scrollable, padding=3)
        f.pack(fill="x", anchor="w", pady=2)
        ttk.Label(f, text=f"{key}:", font=("Helvetica", 10, "bold"), bootstyle="secondary").pack(anchor="w")
        ttk.Label(f, text=str(val), font=("Helvetica", 10), wraplength=380, justify="left").pack(anchor="w")

    btn_action_frame = ttk.Frame(left_panel)
    btn_action_frame.pack(fill="x", side="bottom", pady=(10, 0))

    if wishlist_mode == "added":
        ttk.Button(btn_action_frame, text="⭐ Add to Wishlist", command=lambda: add_to_wishlist(email, isbn), bootstyle="warning").pack(fill="x")
    elif wishlist_mode == "removed":
        ttk.Button(btn_action_frame, text="❌ Remove from Wishlist", command=lambda: remove_from_wishlist(app, email, isbn, revert), bootstyle="danger-outline").pack(fill="x")

    right_panel = ttk.Labelframe(content, text="Reviews & Community Ratings", padding=15, bootstyle="secondary")
    right_panel.pack(side="right", fill="both", expand=True, padx=(10, 0))

    if write_reviews:
        rev_input_frame = ttk.Frame(right_panel)
        rev_input_frame.pack(fill="x", pady=(0, 15))

        ttk.Label(rev_input_frame, text="✍️ Write Your Review", font=("Helvetica", 12, "bold"), bootstyle="info").pack(anchor="w", pady=(0, 5))
        review_text = ttk.Text(rev_input_frame, height=4, wrap="word", font=("Helvetica", 10))
        review_text.pack(fill="x", pady=(0, 5))

        rating_row = ttk.Frame(rev_input_frame)
        rating_row.pack(fill="x", pady=(0, 5))

        ttk.Label(rating_row, text="Rating:", font=("Helvetica", 10, "bold")).pack(side="left", padx=(0, 8))
        rating_var = ttk.StringVar(value="5")
        ttk.Combobox(rating_row, textvariable=rating_var, values=["5 - Excellent", "4 - Good", "3 - Average", "2 - Fair", "1 - Poor"], width=15, state="readonly").pack(side="left")

        def submit_rev():
            raw_rev = review_text.get("1.0", "end").strip()
            if not raw_rev:
                messagebox.showerror("Error", "Please type your review comments.")
                return

            rating_digit = rating_var.get()[0]
            member_user = get_user("Members", email=email)
            reviewer_name = member_user[2] if (member_user and isinstance(member_user, (list, tuple)) and len(member_user) > 2) else email

            res = add_review(isbn, reviewer_name, email, raw_rev, rating_digit)
            if "successfully" in res.lower():
                messagebox.showinfo("Success", "Thank you! Your review has been posted.")
                show_details_page(app, email, revert, isbn, write_reviews, wishlist_mode)
            else:
                messagebox.showerror("Error", res)

        ttk.Button(rating_row, text="Submit Review", command=submit_rev, bootstyle="success").pack(side="right")

    ttk.Label(right_panel, text="Recent Reviews", font=("Helvetica", 11, "bold"), bootstyle="secondary").pack(anchor="w", pady=(5, 5))

    r_canvas = ttk.Canvas(right_panel, highlightthickness=0)
    r_scroll = ttk.Scrollbar(right_panel, orient="vertical", command=r_canvas.yview, bootstyle="round")
    r_inner = ttk.Frame(r_canvas)

    r_win_id = r_canvas.create_window((0, 0), window=r_inner, anchor="nw")
    r_canvas.configure(yscrollcommand=r_scroll.set)

    def on_rc_cfg(e):
        r_canvas.itemconfig(r_win_id, width=e.width)

    def on_rf_cfg(e):
        r_canvas.configure(scrollregion=r_canvas.bbox("all"))

    r_canvas.bind("<Configure>", on_rc_cfg)
    r_inner.bind("<Configure>", on_rf_cfg)

    r_canvas.pack(side="left", fill="both", expand=True)
    r_scroll.pack(side="right", fill="y")
    _bind_mousewheel(r_inner, r_canvas)

    reviews_list = get_reviews(isbn)
    if not reviews_list or not isinstance(reviews_list, list):
        ttk.Label(r_inner, text="No reviews yet for this book.\nBe the first to leave one!", font=("Helvetica", 10, "italic"), bootstyle="secondary").pack(anchor="w", padx=10, pady=10)
    else:
        for r in reviews_list:
            card_f = ttk.Frame(r_inner, padding=8, bootstyle="dark")
            card_f.pack(fill="x", pady=4, padx=5)

            rating_int = max(1, min(5, int(r[4]))) if (len(r) > 4 and r[4] is not None and str(r[4]).isdigit()) else 5
            stars = "★" * rating_int + "☆" * (5 - rating_int)
            top_line = ttk.Frame(card_f)
            top_line.pack(fill="x")
            ttk.Label(top_line, text=f"👤 {r[2]}", font=("Helvetica", 9, "bold"), bootstyle="inverse-dark").pack(side="left")
            ttk.Label(top_line, text=stars, font=("Helvetica", 10, "bold"), bootstyle="warning").pack(side="right")

            ttk.Label(card_f, text=str(r[5]), font=("Helvetica", 9), wraplength=340, justify="left", bootstyle="inverse-dark").pack(fill="x", pady=(3, 0), anchor="w")
