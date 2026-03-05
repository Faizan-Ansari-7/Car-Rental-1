import pandas as pd
from db_connect import get_connection
import streamlit as st

# ==========================================
# 1. READ FUNCTIONS (Fetch Data)
# ==========================================
def view_all_users():
    """Fetches all users for the Admin Panel."""
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT user_id, first_name, last_name, email, phone_number, role FROM users", conn)
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def view_all_bookings():
    """Fetches all bookings for the Admin Panel."""
    conn = get_connection()
    if conn:
        query = """
        SELECT 
            b.booking_id, u.first_name, u.last_name, c.car_name, 
            b.start_date, b.start_time, b.end_date, b.end_time, 
            b.total_price, b.status, b.pickup_location, b.drop_location

        FROM bookings b
        JOIN users u ON b.user_id = u.user_id
        JOIN cars c ON b.car_id = c.car_id
        ORDER BY b.booking_id DESC
        """
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def view_all_cars():
    """Fetches all cars including total_quantity."""
    conn = get_connection()
    if conn:
        df = pd.read_sql("SELECT * FROM cars ORDER BY car_id ASC", conn)
        conn.close()
        return df
    return pd.DataFrame()

def get_user_bookings(user_id):
    """Fetches booking history for a specific user."""
    conn = get_connection()
    if conn:
        if user_id == 'admin': 
             return view_all_bookings()
        
        query = """
            SELECT b.booking_id, c.car_name, b.start_date, b.start_time, 
                   b.end_date, b.end_time, b.total_price, b.status, b.pickup_location, b.drop_location

            FROM bookings b
            JOIN cars c ON b.car_id = c.car_id
            WHERE b.user_id = %s
            ORDER BY b.booking_id DESC
        """
        try:
            df = pd.read_sql(query, conn, params=(user_id,))
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def get_all_car_names():
    """Fetches simple list of cars for Feedback dropdown."""
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT car_id, car_name FROM cars", conn)
            conn.close()
            return df
        except Exception:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

# ==========================================
# 2. VALIDATION CHECKS (Limits & Inventory)
# ==========================================
def check_user_limit(user_id):
    """Returns False if user has 3 or more active bookings."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM bookings WHERE user_id = %s AND status = 'Confirmed'", (user_id,))
        count = cursor.fetchone()[0]
        conn.close()
        if count >= 3:
            return False, f"🚫 Limit Reached: You already have {count} active bookings (Max 3)."
        return True, "Allowed"
    return False, "DB Error"

def check_inventory(car_id, start_date, end_date):
    """Returns False if all 4 cars of this model are booked."""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        # 1. Get Total Quantity
        cursor.execute("SELECT total_quantity FROM cars WHERE car_id = %s", (car_id,))
        row = cursor.fetchone()
        if not row: 
            conn.close()
            return False, "Car not found"
        total_qty = row[0] if row[0] is not None else 4 # Default to 4 if NULL
        
        # 2. Count overlapping bookings
        query = """
            SELECT COUNT(*) FROM bookings 
            WHERE car_id = %s 
            AND status = 'Confirmed'
            AND start_date <= %s AND end_date >= %s
        """
        cursor.execute(query, (car_id, end_date, start_date))
        booked_qty = cursor.fetchone()[0]
        conn.close()
        
        available = total_qty - booked_qty
        if available > 0:
            return True, f"✅ Available ({available} left)"
        else:
            return False, "❌ Sold Out for these dates"
    return False, "DB Error"

# ==========================================
# 3. WRITE FUNCTIONS (Add/Update/Delete)
# ==========================================
def add_booking(car_id, user_id, start_d, end_d, start_t, end_t, total_price, pickup, drop, status):
    conn = get_connection()
    new_id = None

    if conn:
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO bookings (
                    car_id,
                    user_id,
                    start_date,
                    end_date,
                    start_time,
                    end_time,
                    total_price,
                    pickup_location,
                    drop_location,
                    status
                )
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                RETURNING booking_id
            """

            cursor.execute(query, (
                car_id,
                user_id,
                start_d,
                end_d,
                start_t,
                end_t,
                total_price,
                pickup,
                drop,
                status
            ))

            new_id = cursor.fetchone()[0]
            conn.commit()

        except Exception as e:
            st.error(f"Booking Error: {e}")

        finally:
            cursor.close()
            conn.close()

    return new_id


def add_car(name, brand, price, trans, fuel, image):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = """
                INSERT INTO cars (car_name, brand, price_per_day, transmission, fuel_type, image_filename, is_available, total_quantity)
                VALUES (%s, %s, %s, %s, %s, %s, TRUE, 4)
            """
            cursor.execute(query, (name, brand, price, trans, fuel, image))
            conn.commit()
        except Exception as e:
            st.error(f"Error adding car: {e}")
        finally:
            cursor.close()
            conn.close()

def delete_car(car_id):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM cars WHERE car_id = %s", (car_id,))
            conn.commit()
        except Exception as e:
            st.error(f"Error deleting car: {e}")
        finally:
            cursor.close()
            conn.close()

def update_car_price(car_id, new_price):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE cars SET price_per_day = %s WHERE car_id = %s", (new_price, car_id))
            conn.commit()
        except Exception as e:
            st.error(f"Error updating price: {e}")
        finally:
            cursor.close()
            conn.close()

def add_feedback(user_id, car_id, rating, comment):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO reviews (user_id, car_id, rating, comment) VALUES (%s, %s, %s, %s)", 
                           (user_id, car_id, rating, comment))
            conn.commit()
        except Exception:
            pass # Fail silently
        finally:
            cursor.close()
            conn.close()

# ==========================================
# 4. ANALYTICS (Required for Admin Dashboard)
# ==========================================
def get_most_popular_cars():
    conn = get_connection()
    if conn:
        query = """
        SELECT c.car_name, COUNT(b.booking_id) as count
        FROM bookings b
        JOIN cars c ON b.car_id = c.car_id
        GROUP BY c.car_name
        ORDER BY count DESC
        LIMIT 5
        """
        try:
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def get_location_stats():
    conn = get_connection()
    if conn:
        try:
            df = pd.read_sql("SELECT pickup_location, COUNT(*) as count FROM bookings GROUP BY pickup_location", conn)
            conn.close()
            return df
        except:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()

def get_monthly_bookings():
    conn = get_connection()
    if conn:
        try:
            query = "SELECT TO_CHAR(start_date, 'Month') as month, COUNT(*) as count FROM bookings GROUP BY month"
            df = pd.read_sql(query, conn)
            conn.close()
            return df
        except:
            conn.close()
            return pd.DataFrame()
    return pd.DataFrame()