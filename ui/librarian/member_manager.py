import tkinter as tk
import ttkbootstrap as ttk
from tkinter import StringVar, messagebox
from backend.account import delete_user, get_user, redeem_points_mem, signup_user, update_user

def create_popup(title, size="520x420", parent=None):
    popup = ttk.Toplevel(parent) if parent else ttk.Toplevel()
    popup.title(title)
    popup.geometry(size)
    form = ttk.Frame(popup, padding=25)
    form.pack(fill="both", expand=True)
    return popup, form

def open_add_member_popup(app, refresh):
    popup, form = create_popup("Add New Member", "520x460", parent=app)
    ttk.Label(form, text="👥 Add New Library Member", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    name_var = StringVar()
    email_var = StringVar()
    mobile_var = StringVar()
    pwd_var = StringVar()

    fields = [
        ("Full Name", name_var, None),
        ("Email Address", email_var, None),
        ("Mobile (10 digits)", mobile_var, None),
        ("Initial Password", pwd_var, "*"),
    ]

    for label, var, show in fields:
        r = ttk.Frame(form)
        r.pack(fill="x", pady=5)
        ttk.Label(r, text=label, font=("Helvetica", 9, "bold"), width=18).pack(side="left")
        ttk.Entry(r, textvariable=var, font=("Helvetica", 10), show=show).pack(side="left", fill="x", expand=True)

    def submit():
        name = name_var.get().strip()
        email = email_var.get().strip()
        mobile = mobile_var.get().strip()
        pwd = pwd_var.get().strip()

        if not all([name, email, mobile, pwd]):
            messagebox.showerror("Error", "All fields are required.")
            return

        res = signup_user("Members", email, name, pwd, mobile)
        if "successful" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Error", res)

    btn_row = ttk.Frame(form)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Create Member", command=submit, bootstyle="primary").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def update_member_popup(app, data, refresh):
    popup, form = create_popup("Update Member Details", "520x440", parent=app)
    ttk.Label(form, text="✏️ Update Member Profile", font=("Helvetica", 16, "bold"), bootstyle="info").pack(pady=(0, 15))

    email_val = str(data[1])
    name_var = StringVar(value=str(data[2]))
    mobile_var = StringVar(value=str(data[4]))
    new_pwd_var = StringVar()

    ttk.Label(form, text=f"Email: {email_val}", font=("Helvetica", 10, "bold"), bootstyle="secondary").pack(anchor="w", pady=(0, 10))

    fields = [
        ("Full Name", name_var, None),
        ("Mobile Number", mobile_var, None),
        ("Reset Password (optional)", new_pwd_var, "*")
    ]

    for label, var, show in fields:
        r = ttk.Frame(form)
        r.pack(fill="x", pady=5)
        ttk.Label(r, text=label, font=("Helvetica", 9, "bold"), width=22).pack(side="left")
        ttk.Entry(r, textvariable=var, font=("Helvetica", 10), show=show).pack(side="left", fill="x", expand=True)

    def save():
        name = name_var.get().strip()
        mobile = mobile_var.get().strip()
        new_pwd = new_pwd_var.get().strip() or None

        res = update_user("Members", email_val, fullname=name, mobile=mobile, new_password=new_pwd, is_admin=True)
        if "successful" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Error", res)

    btn_row = ttk.Frame(form)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Save Changes", command=save, bootstyle="success").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def remove_points_popup(app, table, refresh):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Selection Required", "Please select a member from the table first.")
        return

    values = table.item(selected[0])["values"]
    email = values[1]
    current_pts = values[4]

    popup, form = create_popup("Redeem / Adjust ProPoints", "460x280", parent=app)
    ttk.Label(form, text=f"🎁 Redeem ProPoints ({email})", font=("Helvetica", 15, "bold"), bootstyle="info").pack(pady=(0, 10))
    ttk.Label(form, text=f"Current Points Balance: {current_pts}", font=("Helvetica", 11, "bold"), bootstyle="success").pack(pady=(0, 15))

    points_var = StringVar()
    r = ttk.Frame(form)
    r.pack(fill="x", pady=5)
    ttk.Label(r, text="Points to Redeem", font=("Helvetica", 9, "bold"), width=18).pack(side="left")
    ttk.Entry(r, textvariable=points_var, font=("Helvetica", 10)).pack(side="left", fill="x", expand=True)

    def save():
        pts = points_var.get().strip()
        res = redeem_points_mem(email, pts)
        if "redeemed" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Error", res)

    btn_row = ttk.Frame(form)
    btn_row.pack(fill="x", pady=(20, 0))
    ttk.Button(btn_row, text="Redeem Points", command=save, bootstyle="warning").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_delete_member_popup(app, table, refresh, admin_email):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Selection Required", "Please select a member from the table first.")
        return

    email = table.item(selected[0])["values"][1]

    popup = ttk.Toplevel(app)
    popup.geometry("420x240")
    popup.title("Confirm Membership Cancellation")

    container = ttk.Frame(popup, padding=25)
    container.pack(fill="both", expand=True)

    ttk.Label(container, text="⚠️ Cancel Member Account", font=("Helvetica", 15, "bold"), bootstyle="danger").pack(pady=(0, 10))
    ttk.Label(container, text=f"Cancel account for:\n{email}", font=("Helvetica", 10), justify="center").pack(pady=(0, 10))

    r = ttk.Frame(container)
    r.pack(fill="x", pady=5)
    ttk.Label(r, text="Admin Password", font=("Helvetica", 9, "bold"), width=16).pack(side="left")
    pwd_entry = ttk.Entry(r, show="*", font=("Helvetica", 10))
    pwd_entry.pack(side="left", fill="x", expand=True)

    def confirm(event=None):
        pwd = pwd_entry.get().strip()
        if not pwd:
            messagebox.showerror("Error", "Admin password is required to delete a member.")
            return

        res = delete_user("Members", email, pwd, librarianEmail=admin_email)
        if "deleted" in res.lower():
            messagebox.showinfo("Success", res)
            popup.destroy()
            refresh()
        else:
            messagebox.showerror("Error", res)

    pwd_entry.bind("<Return>", confirm)

    btn_row = ttk.Frame(container)
    btn_row.pack(fill="x", pady=(15, 0))
    ttk.Button(btn_row, text="Confirm Delete", command=confirm, bootstyle="danger").pack(side="left", padx=5, expand=True, fill="x")
    ttk.Button(btn_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="left", padx=5)

def open_update_member_popup(app, table, refresh):
    selected = table.selection()
    if not selected:
        messagebox.showerror("Selection Required", "Please select a member from the table first.")
        return

    email = table.item(selected[0])["values"][1]
    member = get_user("Members", email=email)
    if member and isinstance(member, (list, tuple)):
        update_member_popup(app, member, refresh)
    else:
        messagebox.showerror("Error", f"Could not fetch details for member {email}.")

def member_manager(app, admin_email):
    container = ttk.Frame(app, padding=15)
    container.pack(fill="both", expand=True)

    top_bar = ttk.Frame(container)
    top_bar.pack(fill="x", pady=(0, 10))

    ttk.Label(top_bar, text="👥 Member Directory & Management", font=("Helvetica", 18, "bold"), bootstyle="info").pack(side="left")

    search_frame = ttk.Frame(top_bar)
    search_frame.pack(side="right")

    search_var = StringVar()
    search_entry = ttk.Entry(search_frame, textvariable=search_var, font=("Helvetica", 10), width=22)
    search_entry.pack(side="left", padx=5)

    table_frame = ttk.Frame(container)
    table_frame.pack(fill="both", expand=True)

    columns = ("Member #", "Email", "Full Name", "Mobile Number", "ProPoints", "Date of Joining")
    table = ttk.Treeview(table_frame, columns=columns, show="headings", bootstyle="secondary")

    widths = {"Member #": 85, "Email": 200, "Full Name": 180, "Mobile Number": 130, "ProPoints": 95, "Date of Joining": 150}
    for col in columns:
        table.heading(col, text=col)
        table.column(col, width=widths.get(col, 120), anchor="center")

    v_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview, bootstyle="round")
    h_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=table.xview, bootstyle="round")
    table.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)

    table.pack(side="left", fill="both", expand=True)
    v_scroll.pack(side="right", fill="y")
    h_scroll.pack(side="bottom", fill="x")

    def populate(query=None):
        table.delete(*table.get_children())
        members = get_user("Members")
        if not members or not isinstance(members, list):
            return

        q = query.lower().strip() if query else ""
        for m in members:
            mem_no = str(m[0])
            email = str(m[1])
            name = str(m[2])
            mobile = str(m[4])
            points = str(m[6] or 0)
            joined = str(m[7])[:10] if m[7] else ""

            if q:
                match = (q in email.lower() or q in name.lower() or q in mobile or q in mem_no)
                if not match:
                    continue

            table.insert("", "end", values=(mem_no, email, name, mobile, points, joined))

    def on_search(event=None):
        populate(search_var.get())

    search_entry.bind("<KeyRelease>", on_search)
    ttk.Button(search_frame, text="🔍 Search", command=on_search, bootstyle="secondary-outline").pack(side="left")

    btn_frame = ttk.Frame(container)
    btn_frame.pack(fill="x", pady=(10, 0))

    ttk.Button(btn_frame, text="➕ Add New Member", command=lambda: open_add_member_popup(app, populate), bootstyle="primary").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="✏️ Update Member", command=lambda: open_update_member_popup(app, table, populate), bootstyle="info").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🎁 Redeem Points", command=lambda: remove_points_popup(app, table, populate), bootstyle="warning").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🗑️ Cancel Membership", command=lambda: open_delete_member_popup(app, table, populate, admin_email), bootstyle="danger-outline").pack(side="left", padx=5)
    ttk.Button(btn_frame, text="🔄 Refresh", command=lambda: [search_var.set(""), populate()], bootstyle="secondary-outline").pack(side="right", padx=5)

    populate()
