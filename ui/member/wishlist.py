import ttkbootstrap as ttk
from backend.books import get_book_det
from backend.account import get_user
from ui.member.show_details import show_details_page
from ui.common import make_scrollable_frame, make_book_card

def wishlist(app, email, db):
    def show_main_page():
        for widget in app.winfo_children():
            widget.destroy()

        wish = get_user(db="Members", email=email, fields=["WishlistedBooks"])
        if not wish or not isinstance(wish, (list, tuple)) or not wish[0]:
            isbns = []
        else:
            isbns = [b.strip() for b in wish[0].split(",") if b.strip()]

        main_frame = ttk.Frame(app, padding=20)
        main_frame.pack(fill="both", expand=True)

        top_bar = ttk.Frame(main_frame)
        top_bar.pack(fill="x", pady=(0, 15))

        ttk.Label(top_bar, text="⭐ My Wishlisted Books", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")
        ttk.Label(top_bar, text=f"({len(isbns)} books saved)", font=("Helvetica", 11), bootstyle="secondary").pack(side="left", padx=10, pady=(4, 0))

        panel = ttk.Frame(main_frame)
        panel.pack(fill="both", expand=True)

        scrollable = make_scrollable_frame(panel)

        if isbns:
            valid_cards = 0
            for i, isbn in enumerate(isbns):
                book_data = get_book_det(isbn=isbn)
                if not book_data or not isinstance(book_data, list):
                    continue
                book = book_data[0]

                card = make_book_card(
                    parent=scrollable,
                    book=book,
                    on_click=lambda current_isbn=isbn: show_details_page(
                        app, email, show_main_page, current_isbn,
                        write_reviews=False, wishlist_mode="removed"
                    )
                )
                row, col = divmod(valid_cards, 4)
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")
                valid_cards += 1

            for c in range(4):
                scrollable.grid_columnconfigure(c, weight=1)

            if valid_cards == 0:
                ttk.Label(scrollable, text="No books currently in your wishlist 📭\nBrowse the catalog to add books to your reading list!", font=("Helvetica", 12), justify="center", bootstyle="secondary").pack(pady=40)
        else:
            ttk.Label(scrollable, text="Your wishlist is empty 📭\nBrowse the library catalog and click 'Add to Wishlist' to save books for later!", font=("Helvetica", 12), justify="center", bootstyle="secondary").pack(pady=40)

    show_main_page()
