import streamlit as st
from car_data import add_car

# --- DATA LIST ---
# Format: (Car Name, Brand, Price, Transmission, Fuel, Image Path)
cars = [
    # 4 SEATERS (Budget & City)
    ("Maruti Swift", "Maruti", 2000, "Manual", "Petrol", "image/swift.png"),
    ("Hyundai Grand i10", "Hyundai", 2200, "Automatic", "Petrol", "image/i10.png"),
    ("Tata Tiago", "Tata", 1800, "Manual", "Petrol", "image/tiago.png"),
    ("Maruti Alto K10", "Maruti", 1500, "Manual", "Petrol", "image/alto.png"),
    ("Renault Kwid", "Renault", 1600, "Manual", "Petrol", "image/kwid.png"),
    ("Maruti Baleno", "Maruti", 2500, "Automatic", "Petrol", "image/baleno.png"),
    
    # 5 SEATERS (Sedans & SUVs)
    ("Hyundai Creta", "Hyundai", 3500, "Automatic", "Diesel", "image/creta.png"),
    ("Kia Seltos", "Kia", 3600, "Manual", "Diesel", "image/seltos.png"),
    ("Honda City", "Honda", 3000, "Automatic", "Petrol", "image/city.png"),
    ("Tata Nexon", "Tata", 3200, "Manual", "Electric", "image/nexon.png"),
    ("Mahindra Thar", "Mahindra", 4500, "Manual", "Diesel", "image/thar.png"),
    ("Hyundai Verna", "Hyundai", 3100, "Automatic", "Petrol", "image/verna.png"),
    
    # 6 SEATERS (Captain Seats)
    ("Maruti XL6", "Maruti", 4000, "Automatic", "Petrol", "image/xl6.png"),
    ("MG Hector Plus", "MG", 4200, "Manual", "Diesel", "image/hector_plus.png"),
    ("Kia Carens", "Kia", 3800, "Automatic", "Diesel", "image/carens.png"),
    ("Hyundai Alcazar", "Hyundai", 4500, "Automatic", "Diesel", "image/alcazar.png"),
    ("Toyota Innova Crysta", "Toyota", 5500, "Manual", "Diesel", "image/crysta.png"),
    ("Tata Safari", "Tata", 5000, "Automatic", "Diesel", "image/safari.png"),

    # 7 SEATERS (Family & Big SUVs)
    ("Toyota Fortuner", "Toyota", 8000, "Automatic", "Diesel", "image/fortuner.png"),
    ("Mahindra Scorpio-N", "Mahindra", 6000, "Manual", "Diesel", "image/scorpio.png"),
    ("Mahindra XUV700", "Mahindra", 6500, "Automatic", "Petrol", "image/xuv700.png"),
    ("Toyota Innova Hycross", "Toyota", 7500, "Automatic", "Hybrid", "image/hycross.png"),
    ("Maruti Ertiga", "Maruti", 3500, "Manual", "CNG", "image/ertiga.png"),
    ("Toyota Rumion", "Toyota", 3600, "Automatic", "Petrol", "image/rumion.png"),
]

# --- EXECUTION ---
print(" Starting Database Injection...")
print(f"Found {len(cars)} cars to add.")

success_count = 0

for car in cars:
    name, brand, price, trans, fuel, img_path = car
    try:
        add_car(name, brand, price, trans, fuel, img_path)
        print(f"Added: {name}")
        success_count += 1
    except Exception as e:
        print(f"Failed to add {name}: {e}")

print("-" * 30)
print(f"Job Done! Successfully added {success_count} cars.")
print("You can now open app.py and see them!")