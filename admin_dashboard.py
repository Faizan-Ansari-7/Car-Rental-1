import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os
from datetime import date

# --- IMPORT DATABASE FUNCTIONS ---
from car_data import (
    view_all_users, 
    view_all_bookings, 
    view_all_cars, 
    add_car, 
    delete_car, 
    update_car_price,
    get_most_popular_cars, 
    get_location_stats, 
    get_monthly_bookings
)

def main():
    try:
        st.set_page_config(page_title="Car Rental Admin", page_icon="🚗", layout="wide")
    except:
        pass
        
    plt.style.use('dark_background')
    st.title("🚗 Car Rental Admin Dashboard")
    
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Dashboard Overview", "Manage Cars", "Manage Bookings", "Analytics"])

    if page == "Dashboard Overview":
        show_dashboard_overview()
    elif page == "Manage Cars":
        show_manage_cars()
    elif page == "Manage Bookings":
        show_manage_bookings()
    elif page == "Analytics":
        show_analytics()

# ==========================================
# 📊 1. DASHBOARD OVERVIEW (SMART LOGIC)
# ==========================================
def show_dashboard_overview():
    st.header("📊 Live Fleet Status")
    
    cars_df = view_all_cars()
    bookings_df = view_all_bookings()
    
    # 1. CALCULATE TOTAL FLEET SIZE (24 Models * 4 Units = 96 Cars)
    # If your DB has a 'total_quantity' column, we use it. Otherwise default to 4.
    if not cars_df.empty:
        if 'total_quantity' in cars_df.columns:
            # Sum up the actual quantities in DB
            total_fleet = cars_df['total_quantity'].fillna(4).sum()
        else:
            # Fallback: 24 cars * 4
            total_fleet = len(cars_df) * 4
    else:
        total_fleet = 0
        
    # 2. CALCULATE "BUSY" CARS (Active Today)
    active_now = 0
    today = date.today()
    
    if not bookings_df.empty:
        # Convert dates to datetime objects for comparison
        bookings_df['start_date'] = pd.to_datetime(bookings_df['start_date']).dt.date
        bookings_df['end_date'] = pd.to_datetime(bookings_df['end_date']).dt.date
        
        # Filter: Status is Confirmed AND Today is between Start & End
        active_mask = (
            (bookings_df['status'] == 'Confirmed') & 
            (bookings_df['start_date'] <= today) & 
            (bookings_df['end_date'] >= today)
        )
        active_now = len(bookings_df[active_mask])
    
    # 3. CALCULATE AVAILABLE
    available_now = int(total_fleet - active_now)
    
    # --- METRICS DISPLAY ---
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Fleet Size", f"{int(total_fleet)} Cars", help="Total physical cars (Models x 4)")
    c2.metric("Rented Out (Today)", f"{active_now} Cars", delta="- Busy", delta_color="inverse")
    c3.metric("Available Now", f"{available_now} Cars", delta="+ Free", delta_color="normal")
    
    # Revenue (Total)
    total_revenue = bookings_df['total_amount'].sum() if not bookings_df.empty else 0
    c4.metric("Total Revenue", f"₹{total_revenue:,.0f}")
    
    st.divider()
    
    # --- SHOW RECENT ACTIVITY ---
    st.subheader("Recent Bookings")
    if not bookings_df.empty:
        # Sort by latest ID
        st.dataframe(bookings_df.sort_values(by='booking_id', ascending=False).head(5), use_container_width=True)
    else:
        st.info("No bookings found.")

# --- 2. MANAGE CARS ---
def show_manage_cars():
    st.header("🚙 Manage Cars")
    IMAGE_FOLDER = "image"
    if not os.path.exists(IMAGE_FOLDER):
        os.makedirs(IMAGE_FOLDER)

    with st.expander("➕ Add New Car Model", expanded=False):
        with st.form("add_car_form"):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Car Model (e.g. Fortuner)")
                brand = st.selectbox("Brand", ["Toyota", "BMW", "Audi", "Hyundai", "Tata", "Mahindra", "Maruti"])
                trans = st.selectbox("Transmission", ["Automatic", "Manual"])
            with col2:
                price = st.number_input("Price per Day (₹)", min_value=500, value=2000)
                fuel = st.selectbox("Fuel Type", ["Petrol", "Diesel", "Electric", "CNG"])
                uploaded_file = st.file_uploader("Upload Car Image", type=["jpg", "png", "jpeg"])
            
            if st.form_submit_button("Add Car"):
                if name and uploaded_file:
                    file_path = os.path.join(IMAGE_FOLDER, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # Add car (Assuming default 4 units in DB logic)
                    add_car(name, brand, price, trans, fuel, file_path)
                    st.success(f"Added {name} successfully!")
                    st.rerun()
                else:
                    st.error("Missing details.")
    
    st.subheader("Current Fleet")
    cars_df = view_all_cars()
    if not cars_df.empty:
        # Show Total Quantity if exists
        if 'total_quantity' not in cars_df.columns:
            cars_df['total_quantity'] = 4 # Visual fallback
            
        st.dataframe(
            cars_df, 
            use_container_width=True,
            column_config={
                "image_filename": st.column_config.ImageColumn("Preview"),
                "total_quantity": st.column_config.NumberColumn("Units", format="%d")
            }
        )
        
        # Delete/Update Options
        c1, c2 = st.columns(2)
        with c1:
            car_list = cars_df['car_name'].unique().tolist()
            if car_list:
                sel_car = st.selectbox("Update Price for", car_list)
                sel_row = cars_df[cars_df['car_name'] == sel_car]
                if not sel_row.empty:
                    sid = sel_row['car_id'].values[0]
                    new_p = st.number_input("New Price", min_value=100)
                    if st.button("Update Price"):
                        update_car_price(int(sid), new_p)
                        st.success("Updated!")
                        st.rerun()
        with c2:
            del_id = st.selectbox("Delete Car ID", cars_df['car_id'].tolist())
            if st.button("Delete Car", type="primary"):
                delete_car(del_id)
                st.rerun()

# --- 3. MANAGE BOOKINGS (Fixed Charts) ---
def show_manage_bookings():
    st.header("📅 Booking Management")
    bookings_df = view_all_bookings()
    
    if not bookings_df.empty:
        st.dataframe(bookings_df, use_container_width=True)
        st.divider()
        
        # Status Chart
        st.subheader("📊 Booking Status")
        status_counts = bookings_df['status'].value_counts()
        if not status_counts.empty:
            fig, ax = plt.subplots(figsize=(8, 3))
            bars = ax.bar(status_counts.index, status_counts.values, color='#ff9f43')
            ax.bar_label(bars, color='white')
            ax.set_title("Booking Status Breakdown")
            st.pyplot(fig)
    else:
        st.info("No bookings available.")

# --- 4. ANALYTICS ---
def show_analytics():
    st.header("📈 Analytics Reports")
    col1, col2 = st.columns(2)
    
    # Popular Cars
    with col1:
        st.subheader("🏆 Popular Cars")
        pop_df = get_most_popular_cars()
        if not pop_df.empty:
            fig, ax = plt.subplots(figsize=(5, 4))
            bars = ax.bar(pop_df['car_name'], pop_df['count'], color='#00d4ff')
            ax.bar_label(bars, color='white')
            plt.xticks(rotation=45, ha='right')
            ax.set_title("Top Rented Models")
            st.pyplot(fig)
        else:
            st.info("No data.")

    # Monthly Trend
    with col2:
        st.subheader("💰 Monthly Trend")
        trend_df = get_monthly_bookings()
        if not trend_df.empty:
            fig, ax = plt.subplots(figsize=(5, 4))
            ax.plot(trend_df['month'], trend_df['count'], marker='o', color='#00ff88')
            ax.fill_between(trend_df['month'], trend_df['count'], color='#00ff88', alpha=0.1)
            ax.set_title("Bookings per Month")
            st.pyplot(fig)
        else:
            st.info("No data.")
            
    # Location
    st.subheader("📍 Location Stats")
    loc_df = get_location_stats()
    if not loc_df.empty:
        fig, ax = plt.subplots(figsize=(6, 3))
        ax.pie(loc_df['count'], labels=loc_df['pickup_location'], autopct='%1.1f%%', 
               colors=['#007bff', '#6610f2', '#6f42c1', '#e83e8c'],
               wedgeprops=dict(width=0.4, edgecolor='white'), textprops={'color':"white"})
        st.pyplot(fig)

if __name__ == "__main__":
    main()