import streamlit as st
from fpdf import FPDF
from datetime import datetime
import os
from db_connect import get_connection


# ==========================================
# PDF DESIGN
# ==========================================
class BillPDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 20)
        self.set_text_color(0, 51, 102)
        self.cell(0, 10, "CAR RENTAL SYSTEM", 0, 1, "C")

        self.ln(5)

        self.set_font("Arial", "I", 10)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, "Premium Mobility Solutions | Invoice", 0, 1, "C")

        self.line(10, 35, 200, 35)
        self.ln(10)


# ==========================================
# SAFE TEXT (prevents unicode crash)
# ==========================================
def clean_text(text):
    return str(text).encode("latin-1", "ignore").decode("latin-1")

# ==========================================
# GENERATE INVOICE (NO IMAGE VERSION)
# ==========================================
def generate_invoice(
    user_name,
    car_name,
    start_date,
    start_time,
    end_date,
    end_time,
    total,
    pickup,
    drop
):

    user_name = clean_text(user_name)
    car_name = clean_text(car_name)
    pickup = clean_text(pickup)
    drop = clean_text(drop)

    pdf = BillPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    booking_date = datetime.today().strftime("%Y-%m-%d")

    pdf.cell(0, 10, f"Date of Issue: {booking_date}", ln=True)
    pdf.ln(5)

    # Customer details
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Customer Details:", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Name: {user_name}", ln=True)
    pdf.ln(3)

    # Rental details
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, "Rental Details:", ln=True)

    pdf.set_font("Arial", size=12)
    pdf.cell(0, 8, f"Vehicle: {car_name}", ln=True)
    pdf.cell(0, 8, f"Pick-up Date: {start_date} at {start_time}", ln=True)
    pdf.cell(0, 8, f"Drop-off Date: {end_date} at {end_time}", ln=True)
    pdf.cell(0, 8, f"Pickup Location: {pickup}", ln=True)
    pdf.cell(0, 8, f"Drop Location: {drop}", ln=True)

    # Total
    pdf.ln(10)
    pdf.set_fill_color(230, 240, 255)
    pdf.rect(10, pdf.get_y(), 190, 20, "F")

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 20, f"TOTAL PAID: Rs. {total}", ln=True)

    # Save file
    safe_name = user_name.replace(" ", "_")
    filename = f"invoice_{safe_name}_{booking_date}.pdf"

    pdf.output(filename)
    return filename

    # ==========================
    # TOTAL SECTION
    # ==========================
    pdf.ln(20)

    pdf.set_fill_color(230, 240, 255)
    pdf.rect(10, pdf.get_y(), 190, 20, "F")

    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 20, f"TOTAL PAID: Rs. {total}", ln=True)

    # ==========================
    # SAVE FILE
    # ==========================
    safe_name = user_name.replace(" ", "_")
    filename = f"invoice_{safe_name}_{booking_date}.pdf"

    pdf.output(filename)
    return filename


# ==========================================
# GET LOCATIONS FROM DATABASE
# ==========================================
def get_locations():
    conn = get_connection()

    if conn:
        cur = conn.cursor()
        cur.execute(
            "SELECT location_id, location_name FROM locations ORDER BY location_name"
        )
        locations = cur.fetchall()
        cur.close()
        conn.close()
        return locations

    return []
