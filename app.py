import streamlit as st
import pandas as pd
import time
import os
from datetime import date, datetime,timedelta
from utils import get_locations

# --- IMPORTS ---
try:
    import login
    import admin_dashboard
    import utils
    from car_data import (view_all_cars, add_booking, add_feedback, 
                          get_all_car_names, get_user_bookings, 
                          check_user_limit, check_inventory)
except ImportError as e:
    st.error(f"⚠️ Critical Error: {e}")
    st.stop()

# --- PAGE CONFIG ---
st.set_page_config(page_title="Car Rental System", page_icon="🚗", layout="wide")

# ==========================================
# 🛠️ SESSION STATE INITIALIZATION
# ==========================================
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'role' not in st.session_state: st.session_state.role = None
if 'user_name' not in st.session_state: st.session_state.user_name = ""
if 'page' not in st.session_state: st.session_state.page = 'home'
if 'selected_car' not in st.session_state: st.session_state.selected_car = None
if 'booking_dates' not in st.session_state: st.session_state.booking_dates = {}
if 'protection_plan' not in st.session_state: st.session_state.protection_plan = False
if 'payment_verified' not in st.session_state: st.session_state.payment_verified = False
if 'final_booking_id' not in st.session_state: st.session_state.final_booking_id = None
if 'return_to_booking' not in st.session_state: st.session_state.return_to_booking = False

# --- LOCATIONS ---
# --- LOCATIONS ---
LOCATIONS = [
    "📍Ahmedabad-SVPI Airport (Domestic T1)",
    "📍Ahmedabad-SVPI Airport (International T2)",
    "📍Ahmedabad-Kalupur Railway Station",
    "📍Ahmedabad-SG Highway (Iscon Cross Road)",
    "📍Surat-International Airport (STV)",
    "📍Surat-Main Railway Station",
    "📍Vadodara-Harni Airport (BDQ)",
    "📍Vadodara-Central Bus Terminal",
    "📍Rajkot-City Centre Hub",
    "📍Mumbai-CSMIA Airport (Terminal 2)",
    "📍Pune-Lohegaon Airport"
]


def navigate_to(page_name):
    st.session_state.page = page_name
    st.rerun()

# ==========================================
# 🔧 SEAT DETECTOR (Updated to catch more cars)
# ==========================================
def get_car_seats(car_name):
    name_lower = car_name.lower()
    
    # 7 Seaters
    if any(x in name_lower for x in ['fortuner', 'scorpio', 'xuv700', 'safari', 'innova', 'ertiga', 'rumion']):
        return 7, "SUV (Family)"
    
    # 6 Seaters
    elif any(x in name_lower for x in ['xl6', 'hector plus', 'alcazar', 'carens']):
        return 6, "Premium MPV"
    
    # 5 Seaters
    elif any(x in name_lower for x in ['creta', 'seltos', 'harrier', 'nexon', 'brezza', 'city', 'verna', 'virtus', 'slavia']):
        return 5, "Compact SUV/Sedan"
    
    # 4 Seaters (Default for Hatchbacks like Swift, i20, etc.)
    else:
        return 4, "Hatchback/Budget"

# ==========================================
# 🏠 PAGE: HOME (Fixed Filter Logic)
# ==========================================
def show_home():
    st.title("🚗 Car Rental System")
    st.divider()
    
    # --- FILTER SECTION ---
    with st.container(border=True):
        f1, f2 = st.columns([1, 3])
        # These names MUST match the 'if' checks below exactly
        filter_option = f1.selectbox("Filter by Type", 
                                     ["All Cars", "7 Seater Family", "6 Seater Premium", "5 Seater SUV", "4 Seater Budget"])
        f2.info(f"⚡ Instant Confirmation Available")

    cars_df = view_all_cars()
    
    if not cars_df.empty:
        cols = st.columns(3)
        for index, car in cars_df.iterrows():
            seats, cat = get_car_seats(car['car_name'])
            
            # --- FILTRATION LOGIC (FIXED) ---
            show_car = True
            
            # 1. 7 Seater Check
            if filter_option == "7 Seater Family" and seats != 7:
                show_car = False
            
            # 2. 6 Seater Check (Fixed String Mismatch)
            if filter_option == "6 Seater Premium" and seats != 6:
                show_car = False
            
            # 3. 5 Seater Check
            if filter_option == "5 Seater SUV" and seats != 5:
                show_car = False
                
            # 4. 4 Seater Check
            if filter_option == "4 Seater Budget" and seats != 4:
                show_car = False
            
            # --- DISPLAY CAR ---
            if show_car:
                with cols[index % 3]:
                    with st.container(border=True):
                        img_path = str(car['image_filename'])
                        if os.path.exists(img_path):
                            st.image(img_path, use_container_width=True)
                        else:
                            st.image("https://via.placeholder.com/300?text=Car", use_container_width=True)
                        
                        st.markdown(f"### {car['car_name']}")
                        st.caption(f"💺 {seats} Seater | ⛽ {car['fuel_type']} | {car['transmission']}")
                        
                        # Price Display
                        c1, c2 = st.columns([1.2, 0.8])
                        with c1:
                            st.markdown(f"**Rate: ₹{car['price_per_day']} / day**")
                        with c2:
                            if st.button("Book Now ➜", key=f"v_{car['car_id']}", use_container_width=True):
                                st.session_state.selected_car = car
                                navigate_to('details')
# ==========================================
# 🔍 PAGE: DETAILS
# ==========================================
def show_details():
    car = st.session_state.selected_car
    st.button("← Back", on_click=lambda: navigate_to('home'))
    st.title(f"{car['car_name']}")
    
    col1, col2 = st.columns([1, 1])
    with col1:
        if os.path.exists(str(car['image_filename'])): st.image(str(car['image_filename']), use_container_width=True)
        qty = car.get('total_quantity', 4)
        st.info(f"**Inventory:** We have {qty} units of this model.")

    with col2:
        st.subheader("📅 Dates & Times")
        st.divider()
        st.subheader("📍 Pickup & Drop Location")

        l1, l2 = st.columns(2)
        with l1:
            pickup_location = st.selectbox("Pickup Location", LOCATIONS)
        with l2:
            drop_location = st.selectbox("Drop Location", LOCATIONS)

        if pickup_location == drop_location:
            st.error("Pickup and Drop location cannot be same")

        st.session_state.pickup_location = pickup_location
        st.session_state.drop_location = drop_location

        # Booking handle karne ka naya function
        def handle_booking(prot, s_date, e_date, s_time, e_time, is_hourly):
            user_id = st.session_state.get('user_id', 'Guest')
            can_book, msg = check_user_limit(user_id)
            if not can_book and st.session_state.logged_in:
                st.error(msg)
                return

            available, inv_msg = check_inventory(car['car_id'], s_date, e_date)
            if not available:
                st.error(inv_msg)
                return

            st.session_state.is_hourly = is_hourly
            process_booking(s_date, e_date, s_time, e_time, prot)

        # 2 Sections (Tabs) Banaye gaye hain
        tab_day, tab_hour = st.tabs(["📅 Day-wise Booking", "⏱️ Hour-wise Booking"])

        # --- DAY-WISE SECTION ---
        with tab_day:
            c_d1, c_d2 = st.columns(2)
            start_date = c_d1.date_input("Start Date", min_value=date.today(), key="day_start")
            min_end_date = start_date + timedelta(days=1)
            end_date = c_d2.date_input("End Date", min_value=min_end_date, value=min_end_date, key="day_end")
            
            c_t1, c_t2 = st.columns(2)
            start_time = c_t1.time_input("Pick-up Time", value=datetime.strptime("10:00", "%H:%M").time(), key="day_t_start")
            end_time = c_t2.time_input("Drop-off Time", value=datetime.strptime("10:00", "%H:%M").time(), key="day_t_end")
            
            days = (end_date - start_date).days
            if days < 1: days = 1 
            
            st.divider()
            st.subheader("🛡️ Protection Plan (Day-wise)")
            
            # Do columns banaye comparison ke liye
            b1, b2 = st.columns(2)
            
            with b1:
                # Without Premium Column
                st.markdown("### 🚙 Without Premium (Basic)")
                st.markdown("""
                * ❌ Zero Damage Liability
                * ❌ 24/7 Roadside Assistance
                * ❌ Third-Party Cover
                * ❌ Priority Replacement
                """)
                
                base_price = days * car['price_per_day']
                st.markdown(f"#### Total: ₹{base_price}")
                if st.button("Book Basic", key="day_basic", use_container_width=True):
                    handle_booking(False, start_date, end_date, start_time, end_time, False)
                    
            with b2:
                # With Premium Column
                st.markdown("### 🛡️ With Premium")
                st.markdown("""
                * ✅ **Zero Damage Liability**
                * ✅ **24/7 Roadside Assistance**
                * ✅ **Third-Party Cover**
                * ✅ **Priority Replacement**
                """)
                
                prot_price = base_price + (500 * days)
                st.markdown(f"#### Total: ₹{prot_price}")
                if st.button("Book Premium 🛡️", key="day_premium", type="primary", use_container_width=True):
                    handle_booking(True, start_date, end_date, start_time, end_time, False)

        # --- HOUR-WISE SECTION ---
        with tab_hour:
            h_date = st.date_input("Select Date", min_value=date.today(), key="hour_date")
            hc1, hc2 = st.columns(2)
            h_start_time = hc1.time_input("Pick-up Time", value=datetime.strptime("10:00", "%H:%M").time(), key="hour_start_t")
            
            # Default end time ko 1 ghanta aage (11:00) set kiya hai taaki default view me error na aaye
            h_end_time = hc2.time_input("Drop-off Time", value=datetime.strptime("11:00", "%H:%M").time(), key="hour_end_t") 
            
            dt_start = datetime.combine(h_date, h_start_time)
            dt_end = datetime.combine(h_date, h_end_time)
            
            # Hours calculate karna
            hours = (dt_end - dt_start).total_seconds() / 3600
            
            # Conditions check karna
            if dt_end <= dt_start:
                st.error("Drop-off time Pick-up time ke baad ka hona chahiye.")
                is_valid_hours = False
            elif hours < 1:
                st.error("⚠️ Minimum booking duration is 1 hour .")
                is_valid_hours = False
            else:
                is_valid_hours = True
                
            hourly_rate = round(car['price_per_day'] / 24)
            
            st.divider()
            st.subheader("🛡️ Protection Plan (Hour-wise)")
            
            hb1, hb2 = st.columns(2)
            
            with hb1:
                # Without Premium Column
                st.markdown("### 🚙 Without Premium (Basic)")
                st.markdown("""
                * ❌ Zero Damage Liability
                * ❌ 24/7 Roadside Assistance
                * ❌ Third-Party Cover
                * ❌ Priority Replacement
                """)
                
                base_price_h = round(hours * hourly_rate) if is_valid_hours else 0
                display_hours = hours if is_valid_hours else 0
                st.markdown(f"#### Total: ₹{base_price_h} ({display_hours:.1f} hrs @ ₹{hourly_rate}/hr)")
                
                if st.button("Book Basic", key="hour_basic", use_container_width=True, disabled=not is_valid_hours):
                    handle_booking(False, h_date, h_date, h_start_time, h_end_time, True)
                    
            with hb2:
                # With Premium Column
                st.markdown("### 🛡️ With Premium")
                st.markdown("""
                * ✅ **Zero Damage Liability**
                * ✅ **24/7 Roadside Assistance**
                * ✅ **Third-Party Cover**
                * ✅ **Priority Replacement**
                """)
                
                prot_price_h = base_price_h + int(50 * hours) if is_valid_hours else 0
                st.markdown(f"#### Total: ₹{prot_price_h}")
                
                if st.button("Book Premium 🛡️", key="hour_premium", type="primary", use_container_width=True, disabled=not is_valid_hours):
                    handle_booking(True, h_date, h_date, h_start_time, h_end_time, True)

def process_booking(start, end, start_t, end_t, protection):
    if start > end:
        st.error("Invalid Dates!")
        return
    st.session_state.booking_dates = {
    "start": start,
    "end": end,
    "start_t": start_t,
    "end_t": end_t,
    "pickup": st.session_state.get("pickup_location"),
    "drop": st.session_state.get("drop_location")
}

    st.session_state.protection_plan = protection
    st.session_state.payment_verified = False 
    
    if st.session_state.logged_in:
        navigate_to('booking')
    else:
        st.warning("Please Login first.")
        st.session_state.return_to_booking = True
        time.sleep(1)
        navigate_to('login')

# ==========================================
# 💳 PAGE: CHECKOUT
# ==========================================
def show_booking():
    car = st.session_state.selected_car
    st.title("💳 Secure Checkout")
    
    col1, col2 = st.columns([1, 1.5]) 
    
    start = st.session_state.booking_dates['start']
    end = st.session_state.booking_dates['end']
    s_time_obj = st.session_state.booking_dates['start_t']
    e_time_obj = st.session_state.booking_dates['end_t']
    
    s_time = s_time_obj.strftime("%H:%M")
    e_time = e_time_obj.strftime("%H:%M")

    has_prot = st.session_state.get('protection_plan', False)
    is_hourly = st.session_state.get('is_hourly', False)
    
    # --- DYNAMIC PRICE CALCULATION ---
    if is_hourly:
        dt_start = datetime.combine(start, s_time_obj)
        dt_end = datetime.combine(end, e_time_obj)
        hours = (dt_end - dt_start).total_seconds() / 3600
        hourly_rate = round(car['price_per_day'] / 24)
        base_total = round(hours * hourly_rate)
        final_total = base_total + (int(50 * hours) if has_prot else 0)
    else:
        days = (end - start).days
        if days < 1: days = 1
        base_total = days * car['price_per_day']
        final_total = base_total + (500 * days if has_prot else 0)

    with col1:
        st.subheader("Summary")
        st.success(f"**Total Payable: ₹{final_total}**")
        st.write(f"🚗 **{car['car_name']}**")
        st.write(f"📅 {start} ({s_time}) to {end} ({e_time})")
        pickup = st.session_state.booking_dates.get("pickup")
        drop = st.session_state.booking_dates.get("drop")

        st.write(f"📍 Pickup: {pickup}")
        st.write(f"📍 Drop: {drop}")
        st.caption("Includes Taxes & Fees")

    with col2:
        if st.session_state.payment_verified:
            # Generate invoice only once
            if "invoice_path" not in st.session_state:

                pickup = st.session_state.booking_dates.get("pickup")
                drop = st.session_state.booking_dates.get("drop")
                # Convert image path to ABSOLUTE path (fix for PDF)
                

                
                # Generate invoice only once
                if "invoice_path" not in st.session_state:

                    pickup = st.session_state.booking_dates.get("pickup")
                    drop = st.session_state.booking_dates.get("drop")
                    # Convert image path to ABSOLUTE path (fix for PDF)

                    st.session_state.invoice_path = utils.generate_invoice(
                        st.session_state.user_name,
                        car['car_name'],
                        str(start),
                        s_time,
                        str(end),
                        e_time,
                        final_total,
                        pickup,
                        drop
                        )


                
            # Download Button
            with open(st.session_state.invoice_path, "rb") as f:
                st.download_button(
                    "⬇️ Download PDF Invoice",
                    data=f,
                    file_name="invoice.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

            st.write("") 
            if st.button("Go to Home", use_container_width=True): 
                navigate_to('home')

        else:
            # --- PAYMENT VIEW ---
            st.subheader("Select Payment Method")
            tab1, tab2 = st.tabs(["💳 Credit Card", "📱 UPI ID"])
            
            with tab1:
                with st.form("card_form"):
                    card_num = st.text_input("Card Number (16 digits)", max_chars=16, placeholder="0000 0000 0000 0000")
                    
                    c1, c2 = st.columns(2)
                    expiry_date = c1.text_input("Expiry Date",placeholder="MM/YY")
                    
                    cvv = c2.text_input("CVV", type="password", max_chars=3, placeholder="123")
                    
                    submitted = st.form_submit_button("Pay Now")
                    
                    if submitted:
                        if not card_num.strip() or not expiry_date.strip() or not cvv.strip():
                            st.error("❌ For payment all details are necessary")
                        elif len(card_num) != 16 or not card_num.isdigit():
                            st.error("⚠️ Invalid Card Number! ")
                        elif len(cvv) != 3 or not cvv.isdigit():
                            st.error("⚠️ Invalid CVV! ")
                        else:
                            process_payment_success(car, start, end, s_time, e_time, final_total)
            with tab2:
                st.info("Enter UPI ID to proceed.")
                
                with st.form("upi_text_form"):
                    upi_id = st.text_input("UPI ID", placeholder="e.g. user@oksbi")
                    
                    if st.form_submit_button("Verify & Pay"):
                        if not upi_id:
                            st.error("Please enter a UPI ID.")
                        elif "@" not in upi_id:
                            st.error("⚠️ Invalid Format: UPI ID must contain '@'.")
                        elif len(upi_id) < 5:
                            st.error("⚠️ Invalid ID: Too short.")
                        else:
                            process_payment_success(car, start, end, s_time, e_time, final_total)

def process_payment_success(car, start, end, s_time, e_time, total_price):
    with st.spinner("Processing Secure Payment..."):
        time.sleep(1.5)

        user_id_to_save = st.session_state.get('user_id', 'admin')
        car_id = int(car['car_id'])

        pickup = st.session_state.booking_dates.get("pickup")
        drop = st.session_state.booking_dates.get("drop")

        bid = add_booking(
            car_id,
            user_id_to_save,
            str(start),
            str(end),
            str(s_time),
            str(e_time),
            float(total_price),
            pickup,
            drop,
            "Confirmed"
        )

        if bid:
            st.session_state.final_booking_id = bid
            st.session_state.payment_verified = True
            st.balloons()
            st.rerun()
        else:
            st.error("Database Error! User ID might be missing.")

# ==========================================
# ⭐ FEEDBACK
# ==========================================
def show_feedback():
    st.title("⭐ Rate Your Experience")
    cars_df = get_all_car_names() 
    if not cars_df.empty:
        car_dict = dict(zip(cars_df['car_name'], cars_df['car_id']))
        with st.form("feedback_form"):
            selected_name = st.selectbox("Car Model", list(car_dict.keys()))
            rating = st.slider("Rating", 1, 5, 5)
            comment = st.text_area("Review")
            if st.form_submit_button("Submit"):
                add_feedback(st.session_state.get('user_id', 'Guest'), car_dict[selected_name], rating, comment)
                st.success("Saved!")
    else:
        st.warning("No cars found.")

# ==========================================
# 📄 MY BOOKINGS
# ==========================================
def show_my_bookings():
    st.title("My Bookings")
    df = get_user_bookings(st.session_state.get('user_id', 'admin'))
    if not df.empty: st.dataframe(df, use_container_width=True)
    else: st.info("No bookings yet.")

# ==========================================
# 🚦 ROUTER & SIDEBAR
# ==========================================
if __name__ == "__main__":
    
    # 1. Login Logic
    if st.session_state.page == 'login':
        login.login_page()
        if st.session_state.logged_in:
            if st.session_state.role == 'Admin': 
                st.session_state.page = 'admin'
                st.rerun()
            elif st.session_state.return_to_booking: 
                st.session_state.return_to_booking = False
                navigate_to('booking')
            else: 
                navigate_to('home')

    # 2. Admin Logic
    elif st.session_state.logged_in and st.session_state.role == 'Admin':
        with st.sidebar:
            st.title("🔧 Admin")
            if st.button("Logout"):
                st.session_state.logged_in = False
                st.session_state.role = None
                st.session_state.page = 'home'
                st.rerun()
        admin_dashboard.main()

    # 3. Customer Logic
    else:
        with st.sidebar:
            st.title("🚗 Menu")
            if st.session_state.logged_in:
                st.write(f"Hi,**{st.session_state.user_name}**")
                
                menu = ["Home", "My Bookings", "Feedback"]
                idx = 0
                if st.session_state.page == 'my_bookings': idx = 1
                elif st.session_state.page == 'feedback': idx = 2
                
                selected = st.radio("Go to", menu, index=idx)
                
                if selected == "Home" and st.session_state.page not in ['home','details','booking']: navigate_to('home')
                elif selected == "My Bookings" and st.session_state.page != 'my_bookings': navigate_to('my_bookings')
                elif selected == "Feedback" and st.session_state.page != 'feedback': navigate_to('feedback')
                
                st.divider()
                if st.button("Logout", type="primary"):
                    st.session_state.logged_in = False
                    st.session_state.page = 'home'
                    st.rerun()
            else:
                st.info("Guest Mode")
                if st.button("Login"): navigate_to('login')
        
        if st.session_state.page == 'home': show_home()
        elif st.session_state.page == 'details': show_details()
        elif st.session_state.page == 'booking': show_booking()
        elif st.session_state.page == 'my_bookings': show_my_bookings()
        elif st.session_state.page == 'feedback': show_feedback()