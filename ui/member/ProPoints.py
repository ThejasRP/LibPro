import ttkbootstrap as ttk
from tkinter import messagebox
from backend.account import get_user, redeem_points_mem

redemption_items = [
    {"name": "Library Tote Bag", "cost": 100, "desc": "Custom canvas tote bag with LibPro insignia"},
    {"name": "Eco Notebook & Pen", "cost": 80, "desc": "Hardcover recycled paper notebook with stylus pen"},
    {"name": "Premium Pen Set", "cost": 50, "desc": "Dual rollerball ink pens in metallic casing"},
    {"name": "Free Book of Choice", "cost": 200, "desc": "Pick any available book from the library catalog"},
    {"name": "Coffee Voucher", "cost": 60, "desc": "One free beverage at the campus library cafe"}
]

def points_dashboard(app, email):
    for widget in app.winfo_children():
        widget.destroy()

    container = ttk.Frame(app, padding=25)
    container.pack(fill="both", expand=True)

    user_data = get_user("Members", email=email)
    current_points = user_data[6] if (user_data and isinstance(user_data, (list, tuple)) and len(user_data) > 6) else 0

    tier = "Bronze Reader" if current_points < 50 else "Silver Reader" if current_points < 100 else "Gold VIP Reader"
    tier_style = "secondary" if current_points < 50 else "info" if current_points < 100 else "warning"

    header_frame = ttk.Frame(container)
    header_frame.pack(fill="x", pady=(0, 20))

    ttk.Label(header_frame, text="🎁 LibPro Rewards & ProPoints", font=("Helvetica", 20, "bold"), bootstyle="info").pack(anchor="w")
    ttk.Label(header_frame, text="Earn points by returning borrowed books on time, then redeem them for exclusive library rewards!", font=("Helvetica", 10), bootstyle="secondary").pack(anchor="w", pady=(2, 0))

    stats_card = ttk.Labelframe(container, text="Your Loyalty Profile", padding=20, bootstyle="primary")
    stats_card.pack(fill="x", pady=(0, 20))

    pts_left = ttk.Frame(stats_card)
    pts_left.pack(side="left", padx=20)
    ttk.Label(pts_left, text="Available ProPoints", font=("Helvetica", 11), bootstyle="secondary").pack(anchor="w")
    points_lbl = ttk.Label(pts_left, text=f"{current_points}", font=("Helvetica", 28, "bold"), bootstyle="success")
    points_lbl.pack(anchor="w")

    pts_right = ttk.Frame(stats_card)
    pts_right.pack(side="right", padx=20)
    ttk.Label(pts_right, text="Membership Tier", font=("Helvetica", 11), bootstyle="secondary").pack(anchor="e")
    ttk.Label(pts_right, text=f"⭐ {tier}", font=("Helvetica", 16, "bold"), bootstyle=tier_style).pack(anchor="e")

    store_frame = ttk.Labelframe(container, text="🏪 Rewards Redemption Store", padding=15, bootstyle="secondary")
    store_frame.pack(fill="both", expand=True)

    items_container = ttk.Frame(store_frame)
    items_container.pack(fill="both", expand=True)

    cols = ("Reward Item", "Description", "Points Cost", "Action")
    tree = ttk.Treeview(items_container, columns=cols, show="headings", bootstyle="info")

    tree.heading("Reward Item", text="Reward Item")
    tree.heading("Description", text="Description")
    tree.heading("Points Cost", text="Points Required")
    tree.heading("Action", text="Eligible")

    tree.column("Reward Item", width=180, anchor="w")
    tree.column("Description", width=340, anchor="w")
    tree.column("Points Cost", width=130, anchor="center")
    tree.column("Action", width=110, anchor="center")

    scroll = ttk.Scrollbar(items_container, orient="vertical", command=tree.yview, bootstyle="round")
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    for item in redemption_items:
        can_afford = "✅ Yes" if current_points >= item["cost"] else "❌ Need More"
        tree.insert("", "end", values=(item["name"], item["desc"], f"{item['cost']} pts", can_afford))

    def on_redeem():
        selected = tree.selection()
        if not selected:
            messagebox.showerror("Selection Required", "Please click on a reward item to redeem.")
            return

        item_idx = tree.index(selected[0])
        item = redemption_items[item_idx]

        fresh_user = get_user("Members", email=email)
        pts = fresh_user[6] if (fresh_user and isinstance(fresh_user, (list, tuple)) and len(fresh_user) > 6) else 0

        if pts < item["cost"]:
            messagebox.showerror("Insufficient Points", f"You need {item['cost']} points to redeem this item, but you currently have {pts} points.")
            return

        confirm = messagebox.askyesno("Confirm Redemption", f"Redeem '{item['name']}' for {item['cost']} points?\nYour new points balance will be {pts - item['cost']}.")
        if confirm:
            res = redeem_points_mem(email, item["cost"])
            if "redeemed" in res.lower():
                messagebox.showinfo("Success 🎉", f"Congratulations! You have redeemed '{item['name']}'!\nPlease claim your reward at the librarian circulation desk.")
                points_dashboard(app, email)
            else:
                messagebox.showerror("Redemption Error", res)

    action_row = ttk.Frame(store_frame)
    action_row.pack(fill="x", pady=(10, 0))
    ttk.Button(action_row, text="🎁 Redeem Selected Reward", command=on_redeem, bootstyle="success").pack(side="left", padx=5)
    ttk.Label(action_row, text="Select an item above and click 'Redeem Selected Reward'", font=("Helvetica", 9, "italic"), bootstyle="secondary").pack(side="left", padx=10)
