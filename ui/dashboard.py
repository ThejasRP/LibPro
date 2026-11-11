import os
import ttkbootstrap as ttk
from tkinter import messagebox
from ttkbootstrap.constants import *
from PIL import Image, ImageTk

from ui.common import get_asset_path
from ui.content import dashboard_content
from ui.librarian.book_record import books_record
from ui.librarian.member_manager import member_manager
from ui.librarian.bay_manage import bay_manager
from ui.librarian.books_manage import books_manage
from ui.member.wishlist import wishlist
from ui.member.view_books import view_books
from ui.member.ProPoints import points_dashboard
from ui.member.view_borrowed_books import view_borrowed_books

def clear_container(container):
    for widget in container.winfo_children():
        widget.destroy()

def open_dashboard(container, user, db):
    clear_container(container)
    dashboard_content(container, user, db)

def open_borrowed_books(container, email):
    clear_container(container)
    view_borrowed_books(container, email)

def open_book_manager(container):
    clear_container(container)
    books_manage(container)

def open_books_record(container, email):
    clear_container(container)
    books_record(container, email)

def open_bay_manager(container):
    clear_container(container)
    bay_manager(container)

def open_member_manager(container, admEmail):
    clear_container(container)
    member_manager(container, admEmail)

def open_view_books(container, email):
    clear_container(container)
    view_books(container, email)

def open_wishlisted_books(container, email):
    clear_container(container)
    wishlist(container, email, "Members")

def open_pro_points(container, user):
    clear_container(container)
    points_dashboard(container, user)

def logout(app):
    if messagebox.askyesno("Confirm Logout", "Are you sure you want to log out of LibPro?"):
        from ui.login import login_screen
        clear_container(app)
        login_screen(app)

def dashboard(app, email, db):
    if not app or db not in ["Librarian", "Members"]:
        messagebox.showerror("Error", "Application instance not found or invalid role.")
        return

    selected_button = {"current": None}

    def select_button(btn):
        if selected_button["current"]:
            selected_button["current"].configure(bootstyle="secondary-outline")
        btn.configure(bootstyle="primary")
        selected_button["current"] = btn

    welcome_frame = ttk.Frame(app)
    welcome_frame.pack(expand=True, fill="both")

    menu_frame = ttk.Frame(welcome_frame, padding=12, bootstyle="dark")
    menu_frame.pack(fill="y", side="left")

    logo_path = get_asset_path("ui", "images", "logo.png")
    if os.path.exists(logo_path):
        img = Image.open(logo_path).resize((150, 50))
        photo = ImageTk.PhotoImage(img)
        logo_label = ttk.Label(menu_frame, image=photo, bootstyle="dark")
        logo_label.image = photo
        logo_label.pack(pady=(10, 15))
    else:
        ttk.Label(menu_frame, text="LibPro", font=("Helvetica", 18, "bold"), bootstyle="inverse-dark").pack(pady=(10, 15))

    role_badge_frame = ttk.Frame(menu_frame, padding=8, bootstyle="secondary")
    role_badge_frame.pack(fill="x", padx=5, pady=(0, 20))
    role_label = "Librarian (Admin)" if db == "Librarian" else "Library Member"
    ttk.Label(role_badge_frame, text=role_label, font=("Helvetica", 9, "bold"), bootstyle="inverse-secondary").pack(anchor="w")
    ttk.Label(role_badge_frame, text=email, font=("Helvetica", 8), bootstyle="inverse-secondary").pack(anchor="w")

    main_frame = ttk.Frame(welcome_frame)
    main_frame.pack(expand=True, fill="both")

    nav_buttons = []
    if db == "Librarian":
        dashboard_btn = ttk.Button(menu_frame, text="📊 Dashboard", bootstyle="secondary-outline",
                                   command=lambda: [select_button(dashboard_btn), open_dashboard(main_frame, email, db)])
        books_btn = ttk.Button(menu_frame, text="📚 Manage Books", bootstyle="secondary-outline",
                               command=lambda: [select_button(books_btn), open_book_manager(main_frame)])
        records_btn = ttk.Button(menu_frame, text="📋 Book Records", bootstyle="secondary-outline",
                                 command=lambda: [select_button(records_btn), open_books_record(main_frame, email)])
        bay_btn = ttk.Button(menu_frame, text="🗄️ Bay Management", bootstyle="secondary-outline",
                             command=lambda: [select_button(bay_btn), open_bay_manager(main_frame)])
        members_btn = ttk.Button(menu_frame, text="👥 Member Manager", bootstyle="secondary-outline",
                                 command=lambda: [select_button(members_btn), open_member_manager(main_frame, email)])

        nav_buttons = [dashboard_btn, books_btn, records_btn, bay_btn, members_btn]
    else:
        dashboard_btn = ttk.Button(menu_frame, text="📊 Dashboard", bootstyle="secondary-outline",
                                   command=lambda: [select_button(dashboard_btn), open_dashboard(main_frame, email, db)])
        books_btn = ttk.Button(menu_frame, text="🔍 Browse Catalog", bootstyle="secondary-outline",
                               command=lambda: [select_button(books_btn), open_view_books(main_frame, email)])
        wishlist_btn = ttk.Button(menu_frame, text="⭐ Wishlist", bootstyle="secondary-outline",
                                  command=lambda: [select_button(wishlist_btn), open_wishlisted_books(main_frame, email)])
        borrowed_btn = ttk.Button(menu_frame, text="📖 Borrowed Books", bootstyle="secondary-outline",
                                  command=lambda: [select_button(borrowed_btn), open_borrowed_books(main_frame, email)])
        points_btn = ttk.Button(menu_frame, text="🎁 ProPoints", bootstyle="secondary-outline",
                                command=lambda: [select_button(points_btn), open_pro_points(main_frame, email)])

        nav_buttons = [dashboard_btn, books_btn, wishlist_btn, borrowed_btn, points_btn]

    for btn in nav_buttons:
        btn.pack(padx=5, pady=4, fill="x")

    logout_btn = ttk.Button(menu_frame, text="🚪 Sign Out", bootstyle="danger-outline", command=lambda: logout(app))
    logout_btn.pack(padx=5, pady=20, fill="x", side="bottom")

    if nav_buttons:
        select_button(nav_buttons[0])
    dashboard_content(main_frame, email, db)
