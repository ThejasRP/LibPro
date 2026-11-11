import os
import tkinter as tk
from tkinter import messagebox
import ttkbootstrap as ttk
from PIL import Image, ImageTk
from backend.account import signin_user, get_user
from backend.sql import get_connection
from ui.dashboard import dashboard
from ui.common import get_asset_path

def login_screen(app):
    global login_frame, email_var, password_var, role_var, show_pwd_var

    login_frame = ttk.Frame(app)
    login_frame.pack(expand=True, fill="both")

    branding = ttk.Frame(login_frame, bootstyle="dark")
    branding.pack(side="left", expand=True, fill="both", padx=20, pady=20)

    img_path = get_asset_path("ui", "images", "banner.png")
    if os.path.exists(img_path):
        img = Image.open(img_path).resize((460, 460))
        photo = ImageTk.PhotoImage(img)
        img_label = ttk.Label(branding, image=photo, bootstyle="dark")
        img_label.image = photo
        img_label.pack(expand=True, pady=30)
    else:
        ttk.Label(branding, text="LibPro", font=("Helvetica", 32, "bold"), bootstyle="inverse-dark").pack(expand=True)

    login_section = ttk.Frame(login_frame, padding=40)
    login_section.pack(side="right", expand=True, fill="both")

    center_container = ttk.Frame(login_section)
    center_container.place(relx=0.5, rely=0.5, anchor="center")

    card = ttk.Labelframe(center_container, padding=30, bootstyle="secondary")
    card.pack(fill="both", expand=True)

    ttk.Label(card, text="LibPro", font=("Helvetica", 28, "bold"), bootstyle="info").pack(pady=(0, 5))
    ttk.Label(card, text="Sign in to your library account", font=("Helvetica", 11), bootstyle="secondary").pack(pady=(0, 20))

    role_frame = ttk.Frame(card)
    role_frame.pack(fill="x", pady=(0, 15))

    role_var = ttk.StringVar(value="Librarian")
    ttk.Radiobutton(role_frame, text="Librarian", variable=role_var, value="Librarian", bootstyle="info-toolbutton").pack(side="left", expand=True, fill="x", padx=3)
    ttk.Radiobutton(role_frame, text="Member", variable=role_var, value="Members", bootstyle="info-toolbutton").pack(side="left", expand=True, fill="x", padx=3)

    email_var = ttk.StringVar()
    password_var = ttk.StringVar()
    show_pwd_var = ttk.BooleanVar(value=False)

    ttk.Label(card, text="Email Address", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))
    email_entry = ttk.Entry(card, textvariable=email_var, font=("Helvetica", 11), width=32)
    email_entry.pack(fill="x", pady=(0, 10))

    ttk.Label(card, text="Password", font=("Helvetica", 10, "bold")).pack(anchor="w", pady=(5, 2))
    password_entry = ttk.Entry(card, textvariable=password_var, font=("Helvetica", 11), show="*", width=32)
    password_entry.pack(fill="x", pady=(0, 5))

    def toggle_show_password():
        password_entry.configure(show="" if show_pwd_var.get() else "*")

    ttk.Checkbutton(card, text="Show Password", variable=show_pwd_var, command=toggle_show_password, bootstyle="round-toggle").pack(anchor="w", pady=(0, 15))

    def trigger_login(event=None):
        validate_login(app)

    email_entry.bind("<Return>", trigger_login)
    password_entry.bind("<Return>", trigger_login)

    login_btn = ttk.Button(card, text="Login", command=trigger_login, bootstyle="primary", width=20)
    login_btn.pack(fill="x", pady=(10, 15))

    ttk.Label(card, text="Welcome to the modern library experience.", font=("Helvetica", 9, "italic"), bootstyle="secondary").pack(pady=(5, 0))

def validate_login(app):
    email = email_var.get().strip()
    password = password_var.get().strip()
    role = role_var.get().strip()

    if not email or not password:
        messagebox.showerror("Error", "Email and password cannot be empty.")
        return

    c = get_connection()
    if not c:
        messagebox.showerror(
            "Database Offline",
            "Could not connect to the MySQL database.\nPlease verify MySQL is running on localhost:3306 and check credentials in db_config.json or backend/sql.py."
        )
        return

    try:
        user_exists = get_user(role, email=email, bool=True)
        if not user_exists:
            alt_role = "Members" if role == "Librarian" else "Librarian"
            if get_user(alt_role, email=email, bool=True):
                role_label = "Librarian" if alt_role == "Librarian" else "Member"
                messagebox.showerror("Role Mismatch", f"This email is registered as a {role_label}.\nPlease switch the role selector to {role_label}.")
                return
            messagebox.showerror("Error", f"No {role[:-1] if role.endswith('s') else role} account found with email '{email}'.")
            return

        result = signin_user(role, email, password)
        if result == "Login successful.":
            messagebox.showinfo("Success", f"{role[:-1] if role.endswith('s') else role} login successful!")
            login_frame.pack_forget()
            login_frame.destroy()
            dashboard(app, email, role)
        else:
            messagebox.showerror("Login Failed", result)
    except Exception as e:
        messagebox.showerror("Error", f"Unexpected error during login: {e}")
