import re
from collections import Counter
from tkinter import Tk, Label, Button, Text, StringVar, Entry, END, messagebox
from tkinter.filedialog import askopenfilename

# Function to find the frequency of words in a file
def find_words_frequency(file_path):
    try:
        # Try to read the file with utf-8 encoding, or fallback to 'latin1' if it fails
        try:
            with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                text = file.read().lower()
        except UnicodeDecodeError:
            with open(file_path, 'r', encoding='latin1') as file:  # Use 'latin1' as a fallback
                text = file.read().lower()

        # Use `re` to find all words (alphanumeric characters only)
        all_words = re.findall(r'\b\w+\b', text)
        word_frequency = Counter(all_words)
        most_common_words = word_frequency.most_common(10)

        # Prepare the result as a formatted string
        result = f"{'Word':<15} {'Count':<5}\n"
        result += "-" * 20 + "\n"
        for word, count in most_common_words:
            result += f"{word:<15} {count:<5}\n"

        return result
    except Exception as e:
        return f"Error: {str(e)}"

# GUI function to handle file selection and display results
def process_file():
    file_path = file_path_entry.get().strip()
    if not file_path:
        messagebox.showerror("Input Error", "Please select or enter a valid file path.")
        return

    result = find_words_frequency(file_path)
    if "Error" in result:
        messagebox.showerror("File Error", result)
    else:
        result_text.delete(1.0, END)  # Clear previous results
        result_text.insert(END, result)

# Function to open a file dialog and set the file path
def browse_file():
    file_path = askopenfilename(filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")])
    if file_path:
        file_path_entry.delete(0, END)
        file_path_entry.insert(0, file_path)

# Create the main window
root = Tk()
root.title("Word Frequency Analyzer")
root.geometry("600x400")
root.resizable(False, False)

# Set a custom style for buttons and labels
style = {
    "label": {"font": ("Arial", 12), "fg": "#333", "bg": "#F9F9F9"},
    "button": {"font": ("Arial", 12), "bg": "#0078D7", "fg": "#FFFFFF", "activebackground": "#005EA6", "borderwidth": 0},
    "entry": {"font": ("Arial", 12), "bg": "#FFFFFF", "fg": "#333", "borderwidth": 2, "relief": "solid"},
    "text": {"font": ("Arial", 10), "bg": "#F9F9F9", "fg": "#333", "borderwidth": 2, "relief": "solid"},
}

# Title Label
Label(root, text="Word Frequency Analyzer", font=("Arial", 16, "bold"), fg="#333", bg="#F9F9F9").pack(pady=15)

# File Path Input
file_path_frame = Label(root, **style["label"])
file_path_frame.pack(pady=10)

Label(file_path_frame, text="File Path:", **style["label"]).grid(row=0, column=0, padx=5)
file_path_entry = Entry(file_path_frame, width=50, **style["entry"])
file_path_entry.grid(row=0, column=1, padx=5)

# Browse Button
browse_button = Button(file_path_frame, text="Browse", command=browse_file, **style["button"])
browse_button.grid(row=0, column=2, padx=5)

# Process Button
process_button = Button(root, text="Analyze", command=process_file, **style["button"])
process_button.pack(pady=10)

# Results Display
result_text = Text(root, height=15, width=60, **style["text"])
result_text.pack(pady=10)

# Run the application
if __name__ == "__main__":
    root.mainloop()