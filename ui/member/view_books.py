import ttkbootstrap as ttk
from backend.books import get_book_det
from backend.constants import GENRE_DETAILS
from ui.member.show_details import show_details_page
from ui.common import make_scrollable_frame, make_book_card
from ui.scanner import open_barcode_scanner

def view_books(app, email):
    search_var = ttk.StringVar()
    genre_filter_var = ttk.StringVar(value="All Genres")

    def show_main_page():
        for w in app.winfo_children():
            w.destroy()

        main = ttk.Frame(app, padding=20)
        main.pack(fill="both", expand=True)

        top_bar = ttk.Frame(main)
        top_bar.pack(fill="x", pady=(0, 15))

        title_box = ttk.Frame(top_bar)
        title_box.pack(side="left")
        ttk.Label(title_box, text="🔍 Browse Catalog", font=("Helvetica", 18, "bold"), bootstyle="info").pack(anchor="w")
        ttk.Label(title_box, text="Explore books available in the LibPro library collection", font=("Helvetica", 9), bootstyle="secondary").pack(anchor="w")

        controls = ttk.Frame(top_bar)
        controls.pack(side="right")

        genres = ["All Genres"] + sorted(list(GENRE_DETAILS))
        genre_combo = ttk.Combobox(controls, textvariable=genre_filter_var, values=genres, width=16, state="readonly")
        genre_combo.pack(side="left", padx=5)

        search_entry = ttk.Entry(controls, textvariable=search_var, font=("Helvetica", 10), width=20)
        search_entry.pack(side="left", padx=5)

        panel = ttk.Frame(main)
        panel.pack(fill="both", expand=True)

        scrollable = make_scrollable_frame(panel)

        def render_cards():
            for child in scrollable.winfo_children():
                child.destroy()

            query = search_var.get().lower().strip()
            selected_genre = genre_filter_var.get()

            books = get_book_det()
            if not books or not isinstance(books, list):
                ttk.Label(scrollable, text="No books available in catalog.", font=("Helvetica", 13, "bold"), bootstyle="secondary").pack(pady=40)
                return

            filtered_books = []
            for b in books:
                isbn = str(b[1])
                title = str(b[2])
                author = str(b[4])
                genre = str(b[6])

                if selected_genre != "All Genres" and genre.lower() != selected_genre.lower():
                    continue

                if query:
                    if not (query in title.lower() or query in author.lower() or query in isbn.lower() or query in genre.lower()):
                        continue

                filtered_books.append(b)

            if not filtered_books:
                ttk.Label(scrollable, text="No matching books found 📭\nTry another search keyword or genre.", font=("Helvetica", 12), justify="center", bootstyle="secondary").pack(pady=40)
                return

            for idx, book in enumerate(filtered_books):
                row, col = divmod(idx, 4)
                card = make_book_card(
                    parent=scrollable,
                    book=book,
                    on_click=lambda isbn=book[1]: show_details_page(
                        app, email, show_main_page, isbn, write_reviews=True, wishlist_mode="added"
                    )
                )
                card.grid(row=row, column=col, padx=8, pady=8, sticky="nsew")

            for i in range(4):
                scrollable.grid_columnconfigure(i, weight=1)

        def on_barcode_scan():
            def on_code_received(scanned_code):
                search_var.set(scanned_code)
                render_cards()
                matched = [b for b in get_book_det() if str(b[1]) == scanned_code]
                if matched:
                    show_details_page(app, email, show_main_page, scanned_code, write_reviews=True, wishlist_mode="added")

            open_barcode_scanner(app, on_code_received, "Scan Book Barcode")

        search_entry.bind("<KeyRelease>", lambda e: render_cards())
        genre_combo.bind("<<ComboboxSelected>>", lambda e: render_cards())

        ttk.Button(controls, text="📷 Scan Barcode", command=on_barcode_scan, bootstyle="info-outline").pack(side="left", padx=3)
        ttk.Button(controls, text="Reset", command=lambda: [search_var.set(""), genre_filter_var.set("All Genres"), render_cards()], bootstyle="secondary-outline").pack(side="left", padx=3)

        render_cards()

    show_main_page()
