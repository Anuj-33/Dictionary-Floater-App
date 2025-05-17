import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import threading
import pyperclip
import keyboard
import requests
import os
import sys

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and PyInstaller bundled exe """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

app_active = True
root = None
icon_window = None
entry = None

ICON_PATH = "dictionary.png"
ICO_PATH = "dictionary.ico"  # For main window icon


def fetch_meaning(word):
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()
        return data[0]["meanings"][0]["definitions"][0]["definition"]
    except Exception:
        return "Meaning not found."


def show_clipboard_meaning():
    if not app_active:
        return
    word = pyperclip.paste().strip()
    if word:
        meaning = fetch_meaning(word)
        messagebox.showinfo(f"Meaning of: {word}", message=meaning)


def toggle_app():
    global app_active
    app_active = not app_active

    if app_active:
        if root:
            root.deiconify()
        if icon_window:
            icon_window.configure(bg='#D4FFD4')
            icon_window.icon_label.config(image=icon_window.icon_img)
    else:
        if root:
            root.withdraw()
        if icon_window:
            icon_window.configure(bg='#FFD4D4')
            icon_window.icon_label.config(image=icon_window.icon_img_gray)


def on_quit():
    try:
        if icon_window:
            icon_window.destroy()
        if root:
            root.destroy()
    except Exception:
        pass
    os._exit(0)


def search_word():
    word = entry.get().strip()
    if word:
        meaning = fetch_meaning(word)
        messagebox.showinfo(f"Meaning of: {word}", message=meaning)


def create_main_window():
    global root, entry
    root = tk.Toplevel()
    root.title("Dictionary Floater")
    root.geometry("270x130+70+400")
    root.attributes("-topmost", True)
    root.configure(bg="#FAFAFF")
    root.resizable(False, False)

    ico_file_path = resource_path(ICO_PATH)
    if os.path.exists(ico_file_path):
        root.iconbitmap(ico_file_path)

    root.protocol("WM_DELETE_WINDOW", root.withdraw)

    label = tk.Label(root, text="Type a word:", font=("Segoe UI", 11, "bold"), bg="#FAFAFF", fg="#222")
    label.pack(pady=(10, 2))

    entry = tk.Entry(root, width=28, font=("Segoe UI", 11))
    entry.pack(pady=5)

    search_btn = tk.Button(root, text="Search", command=search_word, bg="#4285F4", fg="white",
                           font=("Segoe UI", 10, "bold"), bd=0, relief="ridge", padx=8, pady=3,
                           activebackground="#6EA6FF", activeforeground="white", cursor="hand2")
    search_btn.pack(pady=8)

    hint = tk.Label(root, text="Clipboard: Ctrl+Shift+D | Toggle: Ctrl+Shift+T",
                    font=("Segoe UI", 8), bg="#FAFAFF", fg="#999")
    hint.pack(pady=(2, 0))


def create_floating_icon():
    global icon_window

    icon_window = tk.Tk()
    icon_window.overrideredirect(True)
    icon_window.geometry("44x44+10+350")
    icon_window.attributes("-topmost", True)
    icon_window.configure(bg="#D4FFD4")

    # Load icon images
    icon_file_path = resource_path(ICON_PATH)
    if os.path.exists(icon_file_path):
        img = Image.open(icon_file_path).resize((32, 32))
        icon_img = ImageTk.PhotoImage(img)
        img_gray = img.convert("LA").convert("RGBA")
        icon_img_gray = ImageTk.PhotoImage(img_gray)
    else:
        raise FileNotFoundError(f"{ICON_PATH} not found at {icon_file_path}.")


    icon_window.icon_img = icon_img
    icon_window.icon_img_gray = icon_img_gray

    icon_label = tk.Label(icon_window, image=icon_img, bg="#D4FFD4")
    icon_label.pack(expand=True)
    icon_window.icon_label = icon_label

    def drag_start(event):
        icon_window._drag_x = event.x
        icon_window._drag_y = event.y

    def drag_motion(event):
        x = icon_window.winfo_pointerx() - icon_window._drag_x
        y = icon_window.winfo_pointery() - icon_window._drag_y
        icon_window.geometry(f"+{x}+{y}")

    def on_icon_left(event):
        if app_active:
            show_clipboard_meaning()
        else:
            toggle_app()

    def on_icon_right(event):
        menu = tk.Menu(icon_window, tearoff=0)
        menu.add_command(label="Toggle On/Off (Ctrl+Shift+T)", command=toggle_app)
        menu.add_command(label="Clipboard Search (Ctrl+Shift+D)", command=show_clipboard_meaning)
        menu.add_separator()
        menu.add_command(label="Quit", command=on_quit)
        menu.tk_popup(event.x_root, event.y_root)

    icon_label.bind("<Button-1>", on_icon_left)
    icon_label.bind("<Button-3>", on_icon_right)
    icon_window.bind("<ButtonPress-1>", drag_start)
    icon_window.bind("<B1-Motion>", drag_motion)

    icon_window.protocol("WM_DELETE_WINDOW", on_quit)


def hotkey_listener():
    keyboard.add_hotkey("ctrl+shift+d", show_clipboard_meaning)
    keyboard.add_hotkey("ctrl+shift+t", toggle_app)
    keyboard.wait()


if __name__ == "__main__":
    threading.Thread(target=hotkey_listener, daemon=True).start()
    create_floating_icon()
    create_main_window()
    root.mainloop()

