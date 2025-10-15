import pandas as pd
import tkinter as tk
from tkinter import messagebox
import random

# Load Excel file
file_path = 'insert filename here' # change if needed
df = pd.read_excel(file_path)

# Extract questions and answers as lists
questions = df.iloc[:, 0].astype(str).tolist()
answers = df.iloc[:, 1].astype(str).tolist()

# --- State variables ---
current_index = 0
random_mode = False
order = list(range(len(questions)))  # default sequential order
remaining_questions = []
showing_answer = False

# --- Functions ---
def show_question():
    """Display the current question."""
    global showing_answer
    showing_answer = False
    card_label.config(text=questions[current_index])


def flip_card(event=None):
    """Toggle between showing question and answer."""
    global showing_answer
    if showing_answer:
        card_label.config(text=questions[current_index])
        showing_answer = False
    else:
        card_label.config(text=answers[current_index])
        showing_answer = True


# Keep track of history for random mode
history = []
history_pos = -1


def next_question():
    """Move to the next question."""
    global current_index, remaining_questions, history, history_pos, showing_answer

    if random_mode:
        # If we’re not at the end of history, move forward in history
        if history_pos < len(history) - 1:
            history_pos += 1
            current_index = history[history_pos]
        else:
            # Otherwise, pick a new question
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


def prev_question():
    """Move to the previous question."""
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
    """Toggle random/sequential mode."""
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
        random_button.config(text="Mode: Random")
    else:
        history = []
        history_pos = -1
        current_index = 0
        random_button.config(text="Mode: Sequential")

    showing_answer = False
    show_question()

def draw_rounded_rect(canvas, x, y, w, h, r, **kwargs):
    points = [
        x+r, y,
        x+w-r, y,
        x+w, y, x+w, y+r,
        x+w, y+h-r,
        x+w, y+h, x+w-r, y+h,
        x+r, y+h,
        x, y+h, x, y+h-r,
        x, y+r,
        x, y, x+r, y
    ]
    return canvas.create_polygon(points, smooth=True, **kwargs)

def update_sizes(event=None):
    # Ensure geometry information is up to date
    root.update_idletasks()

    canvas_w = card_canvas.winfo_width()
    canvas_h = card_canvas.winfo_height()
    if canvas_w <= 1 or canvas_h <= 1:
        # Canvas not ready yet, try again shortly
        root.after(50, update_sizes)
        return

    # Calculate card size relative to available canvas size
    card_w = min(max(canvas_w * 0.9, 300), max(canvas_w - 20, 80))
    card_h = min(max(canvas_h * 0.75, 250), max(canvas_h - 20, 80))

    # Clear previous background drawing while keeping the embedded label
    card_canvas.delete("card_art")

    # Draw card background with subtle shadow/border in light gray-blue
    shadow_offset = 6

    # Center the card on the canvas
    origin_x = (canvas_w - card_w) / 2
    origin_y = (canvas_h - card_h) / 2

    # Shadow
    card_canvas.create_rectangle(
        origin_x + shadow_offset,
        origin_y + shadow_offset,
        origin_x + card_w + shadow_offset,
        origin_y + card_h + shadow_offset,
        fill="#d7e1f0",
        outline="",
        width=0,
        tags=("card_art", "card_shadow")
    )
    # Card
    draw_rounded_rect(
        card_canvas,
        origin_x,
        origin_y,
        card_w,
        card_h,
        CARD_RADIUS,
        fill=CARD_BG,
        outline="#aebedc",
        width=2,
        tags=("card_art", "card_body")
    )

    # Update label size and position
    card_canvas.coords(card_window, canvas_w / 2, canvas_h / 2)
    card_canvas.itemconfig(
        card_window,
        width=max(card_w - 40, 120),
        height=max(card_h - 40, 120)
    )

    # Update font size based on card height
    font_size = max(min(int(card_h / 25), 24), 14)
    card_label.config(
        font=("Arial", font_size),
        anchor="center",
        justify="center",
        wraplength=max(card_w - 60, 150)
    )

    # Update button font size and padding
    height = root.winfo_height()
    btn_font_size = max(min(int(height / 50), 16), 10)
    btn_font = ("Arial", btn_font_size, "bold")
    for btn in (prev_button, next_button):
        btn.configure(font=btn_font, fg="#222222")
        btn.configure(padx=btn_font_size * 2, pady=btn_font_size)
    # random_button is primary (dark) button, use white text
    random_button.configure(font=btn_font, fg="#FFFFFF")
    random_button.configure(padx=btn_font_size * 2, pady=btn_font_size)

# --- GUI setup ---
root = tk.Tk()
root.title("Quiz Viewer")
root.geometry("550x650")
root.minsize(350, 400)

# --- Gradient-inspired background ---
# Since tkinter doesn't support gradients natively, simulate with a vertical gradient using Canvas
bg_canvas = tk.Canvas(root, highlightthickness=0)
bg_canvas.pack(fill="both", expand=True)
def draw_gradient(canvas, width, height):
    canvas.delete("gradient")
    limit = height
    (r1, g1, b1) = (240, 248, 255)  # AliceBlue
    (r2, g2, b2) = (255, 255, 255)  # White
    for i in range(limit):
        r = int(r1 + (r2 - r1) * i / limit)
        g = int(g1 + (g2 - g1) * i / limit)
        b = int(b1 + (b2 - b1) * i / limit)
        color = f"#{r:02x}{g:02x}{b:02x}"
        canvas.create_line(0, i, width, i, fill=color, tags="gradient")

def on_bg_resize(event):
    draw_gradient(bg_canvas, event.width, event.height)
    bg_canvas.coords(main_window_id, 0, 0)
    bg_canvas.itemconfig(main_window_id, width=event.width, height=event.height)

bg_canvas.bind("<Configure>", on_bg_resize)

# Create a frame on top of bg_canvas to hold widgets
main_frame = tk.Frame(bg_canvas, bg="#f9fbff")
main_frame.pack(fill="both", expand=True)
main_window_id = bg_canvas.create_window(0, 0, anchor="nw", window=main_frame)

# --- Custom Styles ---
CARD_RADIUS = 26
CARD_BG = "#ffffff"
BTN_BG_PRIMARY = "#6ca0dc"  # Soft blue
BTN_BG_SECONDARY = "#b0b8c1"  # Gray
BTN_FG = "#ffffff"
BTN_FG_SECONDARY = "#222222"
BTN_ACTIVE_BG_PRIMARY = "#5a8acb"
BTN_ACTIVE_BG_SECONDARY = "#9aa3aa"

# --- Rounded Card using Canvas ---
card_canvas = tk.Canvas(main_frame, bg="#f9fbff", highlightthickness=0)
card_canvas.pack(padx=0, pady=(30,12), fill="both", expand=True)

# Place a label on top of the card (centered)
card_label = tk.Label(card_canvas, text="", wraplength=500, font=("Arial", 17), bg=CARD_BG, fg="#222", justify="center", anchor="center")
card_window = card_canvas.create_window(0, 0, window=card_label, width=400, height=300, anchor="center")
card_label.bind("<Button-1>", flip_card)

# --- Button styling helper ---
def style_button(btn, primary=True):
    if primary:
        btn.configure(
            bg=BTN_BG_PRIMARY,
            fg="#FFFFFF",
            activebackground=BTN_ACTIVE_BG_PRIMARY,
            activeforeground="#FFFFFF",
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            highlightthickness=0,

        )
    else:
        btn.configure(
            bg=BTN_BG_SECONDARY,
            fg="#222222",
            activebackground=BTN_ACTIVE_BG_SECONDARY,
            activeforeground="#222222",
            relief="flat",
            bd=0,
            padx=20,
            pady=12,
            highlightthickness=0,

        )
    try:
        btn.configure(borderwidth=0)
    except Exception:
        pass

# --- Button Frame at Bottom ---
button_frame = tk.Frame(main_frame, bg="#f9fbff")
button_frame.pack(pady=(10, 26), side="bottom", fill="x")

prev_button = tk.Button(button_frame, text="Previous", command=prev_question)
style_button(prev_button, primary=False)
prev_button.pack(side="left", expand=True, fill="x", padx=18)

next_button = tk.Button(button_frame, text="Next", command=next_question)
style_button(next_button, primary=False)
next_button.pack(side="left", expand=True, fill="x", padx=18)

random_button = tk.Button(main_frame, text="Mode: Sequential", command=toggle_random)
style_button(random_button, primary=True)
random_button.pack(pady=(0,10), side="bottom", fill="x", padx=50)

# Bind resize event to update sizes
root.bind("<Configure>", update_sizes)

# --- Show the first question
show_question()
root.after(0, update_sizes)

root.mainloop()
