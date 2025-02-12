import phonenumbers
from phonenumbers import timezone, carrier, geocoder
from tkinter import Tk, StringVar, messagebox, END, Entry  # Use tk.Entry
from tkinter.ttk import Label, Button, Style
from tkinter.scrolledtext import ScrolledText

def track_phone_number(number):
    try:
        # Parse the phone number
        phone = phonenumbers.parse(number)
        # Check if the number is valid
        if not phonenumbers.is_valid_number(phone):
            return "Invalid phone number."
        # Get time zone information
        time_zones = ', '.join(timezone.time_zones_for_number(phone))
        # Get carrier information
        carrier_name = carrier.name_for_number(phone, 'en') or "Unknown"
        # Get region information
        region = geocoder.description_for_number(phone, 'en') or "Unknown"
        # Extract details
        std_code = phone.country_code
        national_number = phone.national_number
        # Return results as a formatted string
        return (
            f"STD Code: {std_code}\n"
            f"Number: {national_number}\n"
            f"Time Zone: {time_zones}\n"
            f"Carrier: {carrier_name}\n"
            f"Country/Region: {region}"
        )
    except phonenumbers.NumberParseException as e:
        return f"Error parsing phone number: {e}"

def on_track():
    """Handle the tracking when the user clicks the 'Track' button."""
    number = entry_phone.get().strip()
    if not number:
        messagebox.showerror("Input Error", "Please enter a phone number.")
        return
    result = track_phone_number(number)
    if result:
        text_results.delete(1.0, END)  # Clear previous results
        text_results.insert(END, result)

# Create the main window
root = Tk()
root.title("Phone Number Tracker")
root.geometry("500x400")
root.resizable(False, False)
root.configure(bg="#2B2B2B")  # Dark background color

# Set a custom style for buttons and labels
style = Style()
style.theme_use('default')  # Use default theme for better customization
style.configure('TButton', font=('Arial', 12), foreground='white', background='#005F73', borderwidth=0)  # Teal color
style.map('TButton', background=[('active', '#023E4D')])  # Darker shade on hover
style.configure('TLabel', font=('Arial', 12), foreground='white', background='#2B2B2B')  # Labels with white text

# Title Label
Label(root, text="Phone Number Tracker", font=("Arial", 18, "bold"), foreground="#00B4D8", background="#2B2B2B").pack(pady=15)

# Phone Number Input
Label(root, text="Enter Phone Number:", style='TLabel').pack(pady=(10, 5))
entry_phone = Entry(root, width=30, font=("Arial", 12), background="#FFFFFF", foreground="#333333", borderwidth=2, relief="solid")
entry_phone.pack(pady=5)

# Track Button
Button(root, text="Track", command=on_track, style='TButton').pack(pady=15)

# Results Display
Label(root, text="Results:", font=("Arial", 12, "bold"), foreground="#00B4D8", background="#2B2B2B").pack(pady=(10, 5))
text_results = ScrolledText(
    root,
    height=10,
    width=50,
    font=("Arial", 10),
    background="#1E1E1E",  # Dark background for results
    foreground="#FFFFFF",  # White text for results
    borderwidth=2,
    relief="solid"
)
text_results.pack(pady=5)

# Run the application
root.mainloop()