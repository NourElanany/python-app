from tkinter import Tk, Label, Button, StringVar
from time import strftime
import random

# Function to update the clock and date
def update_time():
    current_time = strftime("%H:%M:%S")
    current_date = strftime("%d-%m-%Y")
    time_label.config(text=current_time)
    date_label.config(text=current_date)
    time_label.after(1000, update_time)  # Update every 1 second

# Function to toggle the clock (start/stop)
def toggle_clock():
    global is_running
    if is_running:
        time_label.after_cancel(update_id)  # Stop the clock
        toggle_button.config(text="Start Clock")
    else:
        update_time()  # Restart the clock
        toggle_button.config(text="Stop Clock")
    is_running = not is_running

# Function to change background color randomly
def change_background():
    colors = ["#FF5733", "#33FF57", "#3357FF", "#F3FF33", "#FF33F3", "#33FFF3"]
    window.config(bg=random.choice(colors))
    time_label.config(bg=window.cget("bg"), fg="white")
    date_label.config(bg=window.cget("bg"), fg="white")
    toggle_button.config(bg=window.cget("bg"), fg="white")
    color_button.config(bg=window.cget("bg"), fg="white")

# Initialize the main window
window = Tk()
window.title("Digital Clock")
window.geometry("400x200")
window.resizable(False, False)

# Global variable to control clock state
is_running = True
update_id = None

# Create labels for time and date
time_label = Label(
    window,
    font=("Arial", 48, "bold"),
    bg="#333333",
    fg="green",
    padx=20,
    pady=10,
    relief="flat"
)
time_label.pack(fill="both", expand=True)

date_label = Label(
    window,
    font=("Arial", 16, "bold"),
    bg="#333333",
    fg="green",
    padx=20,
    pady=5,
    relief="flat"
)
date_label.pack(fill="both", expand=True)

# Create buttons for functionality
toggle_button = Button(
    window,
    text="Stop Clock",
    font=("Arial", 12),
    bg="#4CAF50",
    fg="white",
    command=toggle_clock,
    relief="raised",
    activebackground="#45A049",
    activeforeground="white"
)
toggle_button.pack(side="left", padx=10, pady=10)

color_button = Button(
    window,
    text="Change Color",
    font=("Arial", 12),
    bg="#008CBA",
    fg="white",
    command=change_background,
    relief="raised",
    activebackground="#0077b3",
    activeforeground="white"
)
color_button.pack(side="right", padx=10, pady=10)

# Start updating the clock
update_time()

# Run the GUI
window.mainloop()