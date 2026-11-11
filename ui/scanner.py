import os
import sys
import threading
import tkinter as tk
from tkinter import filedialog, messagebox
import ttkbootstrap as ttk
from PIL import Image, ImageTk
import cv2
import zxingcpp
from ui.common import get_asset_path

try:
    import winsound
except ImportError:
    winsound = None

def play_beep():
    if winsound:
        try:
            threading.Thread(target=lambda: winsound.Beep(1200, 150), daemon=True).start()
        except Exception:
            pass

def decode_barcode_image(image_path):
    try:
        pil_img = Image.open(image_path)
        result = zxingcpp.read_barcode(pil_img)
        if result and result.text:
            return result.text.strip(), str(result.format)
    except Exception:
        pass
    return None, None

def decode_cv_frame(frame):
    try:
        results = zxingcpp.read_barcodes(frame)
        if results:
            for res in results:
                if res and res.text:
                    return res.text.strip(), str(res.format), res.position
    except Exception:
        pass
    return None, None, None

def open_barcode_scanner(parent, callback, title="Scan Barcode / ISBN"):
    popup = ttk.Toplevel(parent)
    popup.title(title)
    popup.geometry("620x580")
    popup.minsize(550, 520)

    is_running = {"active": True, "cap": None}

    container = ttk.Frame(popup, padding=20)
    container.pack(fill="both", expand=True)

    header = ttk.Frame(container)
    header.pack(fill="x", pady=(0, 10))
    ttk.Label(header, text=f"📷 {title}", font=("Helvetica", 16, "bold"), bootstyle="info").pack(side="left")

    status_var = ttk.StringVar(value="Ready to scan")
    status_badge = ttk.Label(header, textvariable=status_var, font=("Helvetica", 9, "bold"), bootstyle="secondary-inverse", padding=5)
    status_badge.pack(side="right")

    notebook = ttk.Notebook(container, bootstyle="info")
    notebook.pack(fill="both", expand=True, pady=10)

    cam_tab = ttk.Frame(notebook, padding=10)
    notebook.add(cam_tab, text="🎥 Live Camera Scan")

    video_label = ttk.Label(cam_tab, text="Connecting to camera...", anchor="center", bootstyle="secondary")
    video_label.pack(fill="both", expand=True, pady=5)

    cam_controls = ttk.Frame(cam_tab)
    cam_controls.pack(fill="x", pady=(8, 0))
    ttk.Label(cam_controls, text="Point barcode at camera lens.", font=("Helvetica", 9, "italic"), bootstyle="secondary").pack(side="left")

    file_tab = ttk.Frame(notebook, padding=20)
    notebook.add(file_tab, text="📁 Scan from Image File")

    file_card = ttk.Labelframe(file_tab, text="Upload or Select Barcode Image", padding=15, bootstyle="secondary")
    file_card.pack(fill="both", expand=True)

    preview_label = ttk.Label(file_card, text="No image selected", anchor="center", bootstyle="secondary")
    preview_label.pack(fill="both", expand=True, pady=10)

    file_btn_row = ttk.Frame(file_card)
    file_btn_row.pack(fill="x", pady=10)

    def trigger_success(code_str):
        if not is_running["active"]:
            return
        is_running["active"] = False
        play_beep()
        status_var.set(f"Detected: {code_str}")
        popup.after(200, lambda: [clean_exit(), callback(code_str)])

    def pick_image():
        path = filedialog.askopenfilename(
            parent=popup,
            title="Select Barcode Image",
            filetypes=[("Image Files", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not path:
            return

        try:
            img = Image.open(path)
            img.thumbnail((350, 180))
            photo = ImageTk.PhotoImage(img)
            preview_label.configure(image=photo, text="")
            preview_label.image = photo
        except Exception:
            pass

        code, fmt = decode_barcode_image(path)
        if code:
            status_var.set(f"Scanned: {code} ({fmt})")
            trigger_success(code)
        else:
            messagebox.showerror("Scan Failed", "No barcode recognized in this image.\nPlease ensure the barcode is sharp, well-lit, and uncropped.")

    ttk.Button(file_btn_row, text="📂 Choose Image File...", command=pick_image, bootstyle="primary").pack(side="left", padx=5)

    sample_isbn_path = get_asset_path("ui", "images", "sample_isbn.png")
    if os.path.exists(sample_isbn_path):
        def load_sample():
            code, _ = decode_barcode_image(sample_isbn_path)
            if code:
                trigger_success(code)
        ttk.Button(file_btn_row, text="🧪 Test Sample ISBN", command=load_sample, bootstyle="info-outline").pack(side="left", padx=5)

    sample_sku_path = get_asset_path("ui", "images", "sample_sku.png")
    if os.path.exists(sample_sku_path):
        def load_sample_sku():
            code, _ = decode_barcode_image(sample_sku_path)
            if code:
                trigger_success(code)
        ttk.Button(file_btn_row, text="🧪 Test Sample SKU", command=load_sample_sku, bootstyle="secondary-outline").pack(side="left", padx=5)

    manual_tab = ttk.Frame(notebook, padding=20)
    notebook.add(manual_tab, text="⌨️ USB Handheld Scanner")

    manual_card = ttk.Labelframe(manual_tab, text="Fast Barcode Reader Input", padding=20, bootstyle="secondary")
    manual_card.pack(fill="both", expand=True)

    ttk.Label(manual_card, text="Scan with handheld USB barcode gun or type manually:", font=("Helvetica", 10)).pack(anchor="w", pady=(0, 10))

    manual_var = ttk.StringVar()
    manual_entry = ttk.Entry(manual_card, textvariable=manual_var, font=("Helvetica", 13), width=28)
    manual_entry.pack(fill="x", pady=(0, 15))

    def on_manual_submit(event=None):
        val = manual_var.get().strip()
        if not val:
            messagebox.showerror("Error", "Please scan or enter a barcode string.")
            return
        trigger_success(val)

    manual_entry.bind("<Return>", on_manual_submit)

    ttk.Button(manual_card, text="Confirm Barcode", command=on_manual_submit, bootstyle="success").pack(fill="x", pady=5)
    ttk.Label(manual_card, text="Standard USB barcode scanners automatically send Enter upon scanning.", font=("Helvetica", 9, "italic"), bootstyle="secondary").pack(anchor="w", pady=(10, 0))

    bottom_row = ttk.Frame(container)
    bottom_row.pack(fill="x", pady=(10, 0))
    ttk.Button(bottom_row, text="Cancel", command=popup.destroy, bootstyle="secondary-outline").pack(side="right")

    def clean_exit():
        is_running["active"] = False
        if is_running["cap"] is not None:
            try:
                is_running["cap"].release()
            except Exception:
                pass
            is_running["cap"] = None
        try:
            popup.destroy()
        except Exception:
            pass

    popup.protocol("WM_DELETE_WINDOW", clean_exit)

    def start_camera():
        try:
            # On Windows, DirectShow backend initializes quickly
            backend = cv2.CAP_DSHOW if sys.platform.startswith('win') else cv2.CAP_ANY
            cap = cv2.VideoCapture(0, backend)
            if not cap.isOpened():
                # Fallback to default backend
                cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                video_label.configure(text="Webcam not detected on this machine.\nPlease switch to 'Scan from Image File' or 'USB Handheld Scanner'.")
                return
            is_running["cap"] = cap
            update_camera_frame()
        except Exception as e:
            video_label.configure(text=f"Camera error: {e}")

    def update_camera_frame():
        if not is_running["active"] or is_running["cap"] is None:
            return

        try:
            ret, frame = is_running["cap"].read()
            if ret and frame is not None:
                code, fmt, pos = decode_cv_frame(frame)
                if code:
                    trigger_success(code)
                    return

                h, w = frame.shape[:2]
                cx, cy = w // 2, h // 2
                rw, rh = int(w * 0.7), int(h * 0.5)
                x1, y1 = cx - rw // 2, cy - rh // 2
                x2, y2 = cx + rw // 2, cy + rh // 2
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 200, 255), 2)
                cv2.putText(frame, "Align barcode inside box", (x1 + 10, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 200, 255), 1)

                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                pil_img = Image.fromarray(rgb)
                pil_img.thumbnail((500, 320))
                photo = ImageTk.PhotoImage(pil_img)
                if video_label.winfo_exists():
                    video_label.configure(image=photo, text="")
                    video_label.image = photo
        except Exception:
            pass

        if is_running["active"]:
            try:
                popup.after(35, update_camera_frame)
            except Exception:
                pass

    popup.after(100, start_camera)
    manual_entry.focus_set()
