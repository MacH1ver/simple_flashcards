import json
import pandas as pd
import tkinter as tk
from tkinter import messagebox, ttk
import random
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES

# ------------------------------
# Data Loading and Preparation
# ------------------------------

example_questions = ["Question 1", "Question 2", "Question 3"]
example_answers = ["Answer 1", "Answer 2", "Answer 3"]

df = pd.DataFrame(example_questions, columns=["Questions"])
df['Answers'] = example_answers

# Extract questions and answers
questions = df.iloc[:, 0].astype(str).tolist()
answers = df.iloc[:, 1].astype(str).tolist()

# ------------------------------
# Dropped File Persistence
# ------------------------------
DROPPED_FILES_STORE = Path(__file__).with_name("dropped_files.json")

def _load_persisted_files():
    try:
        data = json.loads(DROPPED_FILES_STORE.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return [str(Path(p)) for p in data]
    except FileNotFoundError:
        return []
    except (json.JSONDecodeError, OSError):
        return []
    return []

dropped_files = _load_persisted_files()

# ------------------------------
# State Variables
# ------------------------------
current_index = 0
random_mode = False
order = list(range(len(questions)))
remaining_questions = []
showing_answer = False
history = []
history_pos = -1

# ------------------------------
# Functions
# ------------------------------
def load_quiz_file(new_file_path):
    """Load quiz questions from a supplied Excel or CSV file."""
    global questions, answers, current_index, random_mode, remaining_questions, history, history_pos, showing_answer
    try:
        file_path = Path(new_file_path)
        suffix = file_path.suffix.lower()
        if suffix == ".xlsx":
            new_df = pd.read_excel(file_path)
        elif suffix == ".csv":
            new_df = pd.read_csv(file_path)
        else:
            raise ValueError("Unsupported file type. Please use a .xlsx or .csv file.")

        questions = new_df.iloc[:, 0].astype(str).tolist()
        answers = new_df.iloc[:, 1].astype(str).tolist()
        current_index = 0
        random_mode = False
        remaining_questions = []
        history = []
        history_pos = -1
        showing_answer = False
        show_question()
        update_card_layout()
        messagebox.showinfo("File Loaded", f"Loaded quiz from:\n{new_file_path}")
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to load file:\n{e}")
        return False

def persist_dropped_files():
    """Write the tracked file list to disk."""
    try:
        DROPPED_FILES_STORE.write_text(
            json.dumps(dropped_files, indent=2),
            encoding="utf-8"
        )
    except OSError as err:
        messagebox.showwarning("Warning", f"Unable to save file history:\n{err}")

def remember_dropped_file(file_path):
    """Append a new file path to the persisted list if needed."""
    normalized = str(Path(file_path).resolve())
    if normalized in dropped_files:
        return
    dropped_files.append(normalized)
    persist_dropped_files()

def show_question():
    """Show the current question."""
    global showing_answer
    showing_answer = False
    card_label.config(text=questions[current_index])

def flip_card(event=None):
    """Flip between question and answer."""
    global showing_answer
    if showing_answer:
        card_label.config(text=questions[current_index])
        showing_answer = False
    else:
        card_label.config(text=answers[current_index])
        showing_answer = True

def next_question(event=None):
    """Go to next question."""
    global current_index, remaining_questions, history, history_pos, showing_answer
    if random_mode:
        if history_pos < len(history) - 1:
            history_pos += 1
            current_index = history[history_pos]
        else:
            if not remaining_questions:
                remaining_questions = list(range(len(questions)))
                random.shuffle(remaining_questions)
            current_index = remaining_questions.pop()
            history.append(current_index)
            history_pos = len(history) - 1
    else:
        current_index = (current_index + 1) % len(questions)
    showing_answer = False
    show_question()

def prev_question(event=None):
    """Go to previous question."""
    global current_index, history_pos, showing_answer
    if random_mode:
        if history_pos > 0:
            history_pos -= 1
            current_index = history[history_pos]
        else:
            messagebox.showinfo("Notice", "No previous question in history.")
    else:
        current_index = (current_index - 1) % len(questions)
    showing_answer = False
    show_question()

def toggle_random():
    """Toggle between random and sequential modes."""
    global random_mode, current_index, remaining_questions, history, history_pos, showing_answer
    random_mode = not random_mode
    if random_mode:
        remaining_questions = list(range(len(questions)))
        random.shuffle(remaining_questions)
        history = []
        history_pos = -1
        current_index = remaining_questions.pop()
        history.append(current_index)
        history_pos = 0
    else:
        history = []
        history_pos = -1
        current_index = 0
    showing_answer = False
    update_mode_label()
    show_question()

# ------------------------------
# GUI Setup
# ------------------------------
root = TkinterDnD.Tk()
root.title("Quiz Viewer")
root.geometry("550x650")
root.minsize(350, 400)

main_frame = ttk.Frame(root, padding=12)
main_frame.pack(fill="both", expand=True)

# ------------------------------
# Top Bar
# ------------------------------
top_bar = ttk.Frame(main_frame)
top_bar.pack(fill="x")

spacer = ttk.Frame(top_bar)
spacer.pack(side="left", expand=True, fill="x")

mode_label = ttk.Label(top_bar, text="")
mode_label.pack(side="right", padx=(0, 4))

hamburger_button = ttk.Button(top_bar, text="☰")
hamburger_button.pack(side="right")

# Function to update the mode label's text
def update_mode_label():
    if random_mode:
        mode_label.config(text="Random")
    else:
        mode_label.config(text="Sequential")

# Menu
menu = tk.Menu(root, tearoff=0)
menu.add_command(label="Toggle Random/Sequential Mode", command=toggle_random)
menu.add_command(label="Show Dropped Files")
menu.add_command(label="Show/Hide File Drop Area")

def show_menu(event):
    """Display the dropdown menu."""
    x = event.x_root - menu.winfo_reqwidth()
    y = event.y_root
    menu.post(x, y)

hamburger_button.bind("<Button-1>", show_menu)

# ------------------------------
# Drag-and-Drop File Area
# ------------------------------
overlay_visible = False

def on_drop(event):
    """Handle file drop event."""
    data = event.data.strip()
    if data.startswith("{") and data.endswith("}"):
        data = data[1:-1]
    file_paths = data.split()
    file_path_dropped = file_paths[0]
    suffix = Path(file_path_dropped).suffix.lower()
    if suffix in {".xlsx", ".csv"}:
        if load_quiz_file(file_path_dropped):
            remember_dropped_file(file_path_dropped)
            if overlay_visible:
                hide_overlay()
    else:
        messagebox.showerror("Invalid File", "Please drop a valid .xlsx or .csv file.")

# Overlay for focused drop mode
overlay = tk.Toplevel(root)
overlay.withdraw()
overlay.overrideredirect(True)
overlay.attributes("-alpha", 0.75)
overlay.configure(bg="#000000")
overlay_visible = False

overlay_container = ttk.Frame(overlay, padding=24)
overlay_container.pack(expand=True, fill="both")

overlay_label = ttk.Label(
    overlay_container,
    text="Drop .xlsx or .csv quiz file anywhere in this window",
    anchor="center",
    justify="center"
)
overlay_label.pack(expand=True)

overlay_button_frame = ttk.Frame(overlay_container)
overlay_button_frame.pack(fill="x", pady=(12, 0))

overlay.drop_target_register(DND_FILES)
overlay.dnd_bind("<<Drop>>", on_drop)

def update_overlay_geometry(event=None):
    if not overlay_visible:
        return
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = root.winfo_rootx()
    y = root.winfo_rooty()
    overlay.geometry(f"{width}x{height}+{x}+{y}")

def show_overlay():
    """Display the overlay and dim the main window."""
    global overlay_visible
    if overlay_visible:
        return
    overlay_visible = True
    update_overlay_geometry()
    overlay.deiconify()
    overlay.lift()
    overlay.focus_set()

def hide_overlay():
    """Hide the overlay and return focus to the main window."""
    global overlay_visible
    if not overlay_visible:
        return
    overlay.withdraw()
    overlay_visible = False
    root.after_idle(root.focus_force)

close_overlay_button = ttk.Button(
    overlay_button_frame,
    text="Close",
    command=hide_overlay
)
close_overlay_button.pack(side="right")

root.bind("<Configure>", update_overlay_geometry)
root.bind("<Escape>", lambda event: hide_overlay())

def toggle_drop_area(force_hide=False, _event=None):
    """Toggle the full-screen drop overlay."""
    if force_hide:
        hide_overlay()
    elif overlay_visible:
        hide_overlay()
    else:
        show_overlay()

def show_dropped_files():
    """Display a dialog listing all remembered files."""
    if not dropped_files:
        messagebox.showinfo("Saved Files", "No files have been dropped yet.")
        return

    dialog = tk.Toplevel(root)
    dialog.title("Saved Quiz Files")
    dialog.transient(root)
    dialog.grab_set()

    container = ttk.Frame(dialog, padding=12)
    container.pack(fill="both", expand=True)

    header = ttk.Label(container, text="Select a file to load:")
    header.pack(anchor="w", pady=(0, 6))

    listbox = tk.Listbox(container, selectmode=tk.SINGLE, activestyle="none")
    for stored_path in dropped_files:
        listbox.insert(tk.END, Path(stored_path).name)
    listbox.pack(fill="both", expand=True)

    detail_var = tk.StringVar(value="Full path will appear here after selecting an item.")
    detail_label = ttk.Label(
        container,
        textvariable=detail_var,
        justify="left",
        anchor="w",
        wraplength=380
    )
    detail_label.pack(fill="x", pady=(6, 0))

    def update_detail(event=None):
        selection = listbox.curselection()
        if not selection:
            return
        detail_var.set(dropped_files[selection[0]])

    def load_selected():
        selection = listbox.curselection()
        if not selection:
            messagebox.showinfo("Select File", "Please choose a file from the list.")
            return
        selected_path = dropped_files[selection[0]]
        if load_quiz_file(selected_path):
            dialog.destroy()

    action_frame = ttk.Frame(container)
    action_frame.pack(fill="x", pady=(12, 0))

    load_btn = ttk.Button(action_frame, text="Load Selected File", command=load_selected)
    load_btn.pack(side="left")

    close_btn = ttk.Button(action_frame, text="Close", command=dialog.destroy)
    close_btn.pack(side="right")

    listbox.bind("<<ListboxSelect>>", update_detail)
    listbox.bind("<Double-Button-1>", lambda _event: load_selected())
    if dropped_files:
        listbox.selection_set(0)
    update_detail()

    dialog.wait_window()

menu.entryconfig("Show Dropped Files", command=show_dropped_files)
menu.entryconfig("Show/Hide File Drop Area", command=toggle_drop_area)

# ------------------------------
# Card Setup
# ------------------------------
CARD_RADIUS = 26
CARD_BG = "#ffffff"
CARD_OUTLINE = "#aebedc"
CARD_SHADOW = "#d7e1f0"

card_canvas = tk.Canvas(
    main_frame,
    bg=root.cget("bg"),
    highlightthickness=0,
    bd=0,
)
card_canvas.pack(pady=12, fill="both", expand=True)

card_label = tk.Label(
    card_canvas,
    text="",
    wraplength=500,
    font=("Arial", 17),
    bg=CARD_BG,
    fg="#222",
    justify="center",
    anchor="center"
)
card_window = card_canvas.create_window(0, 0, window=card_label, anchor="center")
card_label.bind("<Button-1>", flip_card)

def draw_rounded_rect(canvas, x, y, w, h, r, **kwargs):
    """Draw a rounded rectangle on the canvas."""
    points = [
        x + r, y,
        x + w - r, y,
        x + w, y, x + w, y + r,
        x + w, y + h - r,
        x + w, y + h, x + w - r, y + h,
        x + r, y + h,
        x, y + h, x, y + h - r,
        x, y + r,
        x, y, x + r, y
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def update_card_layout(event=None):
    """Resize and redraw the quiz card."""
    root.update_idletasks()
    canvas_w = card_canvas.winfo_width()
    canvas_h = card_canvas.winfo_height()
    if canvas_w <= 1 or canvas_h <= 1:
        root.after(50, update_card_layout)
        return

    card_w = min(max(canvas_w * 0.9, 300), max(canvas_w - 20, 80))
    card_h = min(max(canvas_h * 0.75, 250), max(canvas_h - 20, 80))

    origin_x = (canvas_w - card_w) / 2
    origin_y = (canvas_h - card_h) / 2

    card_canvas.delete("card_art")
    shadow_offset = 6
    card_canvas.create_rectangle(
        origin_x + shadow_offset,
        origin_y + shadow_offset,
        origin_x + card_w + shadow_offset,
        origin_y + card_h + shadow_offset,
        fill=CARD_SHADOW,
        outline="",
        width=0,
        tags=("card_art", "card_shadow")
    )
    draw_rounded_rect(
        card_canvas,
        origin_x,
        origin_y,
        card_w,
        card_h,
        CARD_RADIUS,
        fill=CARD_BG,
        outline=CARD_OUTLINE,
        width=2,
        tags=("card_art", "card_body")
    )

    card_canvas.coords(card_window, canvas_w / 2, canvas_h / 2)
    card_canvas.itemconfig(
        card_window,
        width=max(card_w - 40, 120),
        height=max(card_h - 40, 120)
    )

    font_size = max(min(int(card_h / 25), 24), 14)
    card_label.config(
        font=("Arial", font_size),
        wraplength=max(card_w - 60, 150)
    )

card_canvas.bind("<Configure>", update_card_layout)

# ------------------------------
# Navigation Buttons
# ------------------------------
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=(0, 12), fill="x")

prev_button = ttk.Button(button_frame, text="Previous", command=prev_question)
next_button = ttk.Button(button_frame, text="Next", command=next_question)
prev_button.pack(side="left", expand=True, fill="x", padx=18)
next_button.pack(side="left", expand=True, fill="x", padx=18)

# ------------------------------
# Start
# ------------------------------
show_question()
update_mode_label()
root.after(0, update_card_layout)

# Keyboard navigation
root.bind("<Right>", next_question)
root.bind("<Left>", prev_question)
root.bind("<Up>", flip_card)
root.bind("<Down>", flip_card)

root.mainloop()
