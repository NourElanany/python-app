from gtts import gTTS
import PyPDF2
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import threading

# Function to convert PDF to text
def pdf_to_text(pdf_path):
    try:
        with open(pdf_path, 'rb') as pdf_file:
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            text_list = []
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text = page.extract_text()
                if text:
                    text_list.append(text)
            return "\n".join(text_list)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to read PDF: {e}")
        return ""

# Function to convert text to audio
def text_to_audio(text, output_path):
    try:
        my_audio = gTTS(text=text, lang='en', slow=False)
        my_audio.save(output_path)
        return True
    except Exception as e:
        messagebox.showerror("Error", f"Failed to create audio: {e}")
        return False

# Function to open file browser
def browse_file():
    file_path = filedialog.askopenfilename(
        title="Select a PDF file",
        filetypes=[("PDF files", "*.pdf")]
    )
    if file_path:
        entry_path.delete(0, tk.END)
        entry_path.insert(0, file_path)

# Conversion process with threading
def start_conversion():
    pdf_path = entry_path.get().strip()
    if not pdf_path:
        messagebox.showwarning("Warning", "Please select a PDF file.")
        return
    
    button_convert.config(state=tk.DISABLED)
    status_label.config(text="Processing...", foreground="#2c3e50")
    
    def conversion_task():
        text = pdf_to_text(pdf_path)
        if not text:
            root.after(0, lambda: messagebox.showwarning("Warning", "No text extracted from the PDF."))
            root.after(0, update_ui)
            return
        
        output_path = filedialog.asksaveasfilename(
            title="Save Audio As",
            defaultextension=".mp3",
            filetypes=[("MP3 files", "*.mp3")]
        )
        
        if output_path:
            status_label.config(text="Converting to audio...")
            success = text_to_audio(text, output_path)
            if success:
                root.after(0, lambda: messagebox.showinfo("Success", f"Audio saved successfully!\n{output_path}"))
        
        root.after(0, update_ui)
    
    threading.Thread(target=conversion_task, daemon=True).start()

def update_ui():
    button_convert.config(state=tk.NORMAL)
    status_label.config(text="Ready")

# Create the GUI
root = tk.Tk()
root.title("PDF to Audio Converter")
root.geometry("600x400")
root.configure(bg="#ecf0f1")

# Custom style configuration
style = ttk.Style()
style.configure("TFrame", background="#ecf0f1")
style.configure("TButton", font=("Helvetica", 12), padding=10)
style.map("TButton", 
          background=[('active', '#3498db'), ('!disabled', '#2980b9')],
          foreground=[('!disabled', 'white')])

# Main container
main_frame = ttk.Frame(root, padding=20)
main_frame.pack(expand=True, fill=tk.BOTH)

# Title
title_label = ttk.Label(main_frame, 
                       text="PDF to Audio Converter",
                       font=("Helvetica", 20, "bold"),
                       background="#ecf0f1",
                       foreground="#2c3e50")
title_label.pack(pady=20)

# File selection frame
file_frame = ttk.Frame(main_frame)
file_frame.pack(fill=tk.X, pady=10)

entry_path = ttk.Entry(file_frame, width=40, font=("Helvetica", 12))
entry_path.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)

browse_btn = ttk.Button(file_frame, text="Browse PDF", command=browse_file)
browse_btn.pack(side=tk.LEFT, padx=5)

# Convert button
button_convert = ttk.Button(main_frame, 
                           text="Convert to MP3", 
                           command=start_conversion,
                           style="TButton")
button_convert.pack(pady=20)

# Status label
status_label = ttk.Label(main_frame, 
                        text="Ready",
                        font=("Helvetica", 10),
                        foreground="#7f8c8d",
                        background="#ecf0f1")
status_label.pack()

# Footer
footer_label = ttk.Label(root, 
                        text="Developed by [Your Name]", 
                        foreground="#7f8c8d",
                        background="#ecf0f1")
footer_label.pack(side=tk.BOTTOM, pady=10)

root.mainloop()