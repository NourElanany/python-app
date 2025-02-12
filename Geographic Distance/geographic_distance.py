from tkinter import Tk, Label, Entry, Button, StringVar, messagebox
from geopy.distance import geodesic

def calculate_distance_and_time(coord1, coord2, avg_speed):
    """
    Calculate the distance between two coordinates and estimate travel time.
    :param coord1: Tuple containing the latitude and longitude of the first location (lat1, lon1)
    :param coord2: Tuple containing the latitude and longitude of the second location (lat2, lon2)
    :param avg_speed: Average speed in km/h for estimating travel time
    :return: Distance in kilometers and estimated travel time in hours
    """
    try:
        # Calculate geodesic distance
        distance = geodesic(coord1, coord2).kilometers
        # Estimate travel time (distance / speed)
        travel_time = distance / avg_speed
        return distance, travel_time
    except Exception as e:
        return None, str(e)

def validate_coordinates(lat, lon):
    """
    Validate if the coordinates are within valid ranges.
    """
    try:
        lat = float(lat)
        lon = float(lon)
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            return False
        return True
    except ValueError:
        return False

def calculate():
    """
    Handle the calculation when the user clicks the 'Calculate' button.
    """
    try:
        # Get input values
        lat1 = entry_lat1.get().strip()
        lon1 = entry_lon1.get().strip()
        lat2 = entry_lat2.get().strip()
        lon2 = entry_lon2.get().strip()
        avg_speed = entry_speed.get().strip()

        # Validate inputs
        if not all([lat1, lon1, lat2, lon2, avg_speed]):
            messagebox.showerror("Input Error", "All fields are required.")
            return

        avg_speed = float(avg_speed)
        if avg_speed <= 0:
            messagebox.showerror("Input Error", "Average speed must be greater than 0.")
            return

        if not validate_coordinates(lat1, lon1) or not validate_coordinates(lat2, lon2):
            messagebox.showerror("Input Error", "Invalid coordinates. Latitude must be between -90 and 90, and longitude must be between -180 and 180.")
            return

        # Parse coordinates
        coord1 = (float(lat1), float(lon1))
        coord2 = (float(lat2), float(lon2))

        # Perform calculation
        distance, travel_time = calculate_distance_and_time(coord1, coord2, avg_speed)

        if distance is None:
            messagebox.showerror("Calculation Error", f"An error occurred: {travel_time}")
            return

        # Update result labels
        result_distance.config(text=f"Distance: {distance:.2f} km")
        result_time.config(text=f"Travel Time: {travel_time:.2f} hours")

    except Exception as e:
        messagebox.showerror("Error", str(e))

# Create the main window
root = Tk()
root.title("Geographic Distance Calculator")
root.geometry("400x300")
root.resizable(False, False)

# Labels
Label(root, text="Enter Coordinates:", font=("Arial", 12)).pack(pady=5)

# First Location
Label(root, text="Latitude 1:").pack(anchor="w", padx=10)
entry_lat1 = Entry(root)
entry_lat1.pack(fill="x", padx=10)

Label(root, text="Longitude 1:").pack(anchor="w", padx=10)
entry_lon1 = Entry(root)
entry_lon1.pack(fill="x", padx=10)

# Second Location
Label(root, text="Latitude 2:").pack(anchor="w", padx=10)
entry_lat2 = Entry(root)
entry_lat2.pack(fill="x", padx=10)

Label(root, text="Longitude 2:").pack(anchor="w", padx=10)
entry_lon2 = Entry(root)
entry_lon2.pack(fill="x", padx=10)

# Average Speed
Label(root, text="Average Speed (km/h):").pack(anchor="w", padx=10)
entry_speed = Entry(root)
entry_speed.pack(fill="x", padx=10)

# Calculate Button
Button(root, text="Calculate", command=calculate).pack(pady=10)

# Result Labels
result_distance = Label(root, text="", font=("Arial", 12), fg="green")
result_distance.pack(pady=5)

result_time = Label(root, text="", font=("Arial", 12), fg="green")
result_time.pack(pady=5)

# Run the application
root.mainloop()