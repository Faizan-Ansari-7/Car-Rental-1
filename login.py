import streamlit as st
import time
import re
from db_connect import get_connection

# --- 1. VALIDATION HELPERS ---
def validate_inputs(email, phone):
    if not re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email):
        return False, "⚠️ Invalid Email format. Example: user@gmail.com"
    
    if not re.match(r"^\d{10}$", phone):
        return False, "⚠️ Invalid Phone. Must be exactly 10 digits."
        
    return True, "Valid"

# --- 2. DATABASE FUNCTIONS ---

def create_user(user_id, first_name, last_name, email, phone, password):
    conn = get_connection()
    msg = ""
    success = False
    
    if conn:
        cursor = conn.cursor()
        try:
            query = """INSERT INTO users 
                       (user_id, first_name, last_name, email, phone_number, password, role) 
                       VALUES (%s, %s, %s, %s, %s, %s, %s)"""
            cursor.execute(query, (user_id, first_name, last_name, email, phone, password, 'Customer'))
            conn.commit()
            success = True
            msg = "✅ Account created successfully!"
        except Exception as e:
            error_str = str(e).lower()
            if "duplicate key" in error_str:
                if "users_pkey" in error_str:
                    msg = "⚠️ This User ID is already taken."
                elif "users_email_key" in error_str:
                    msg = "⚠️ This Email is already registered."
                elif "users_phone_number_key" in error_str: # Assuming phone is unique
                    msg = "⚠️ This Phone Number is already registered."
                else:
                    msg = "⚠️ Account already exists."
            else:
                msg = "❌ System error during signup."
        finally:
            cursor.close()
            conn.close()
            
        return success, msg
    else:
        return False, "❌ Server connection failed."

def login_user(identifier, password):
    conn = get_connection()
    role = None
    f_name = None
    user_id_found = None
    success = False
    msg = ""

    if conn:
        cursor = conn.cursor()
        try:
            # CHECK BOTH USER_ID AND PHONE_NUMBER
            query = """
                SELECT user_id, password, role, first_name 
                FROM users 
                WHERE user_id = %s OR phone_number = %s
            """
            cursor.execute(query, (identifier, identifier))
            result = cursor.fetchone()
            
            if result:
                db_user_id = result[0]
                stored_password = result[1]
                db_role = result[2]
                db_name = result[3]
                
                if password == stored_password:
                    success = True
                    role = db_role
                    f_name = db_name
                    user_id_found = db_user_id
                    msg = f"✅ Welcome back, {f_name}!"
                else:
                    msg = "⚠️ Incorrect Password."
            else:
                msg = "⚠️ Account not found."
                
        except Exception as e:
            msg = f"❌ Login Error: {e}"
        finally:
            cursor.close()
            conn.close()
            
        return success, role, f_name, user_id_found, msg
    else:
        return False, None, None, None, "❌ Server connection failed."

def verify_reset_details(identifier, email):
    """Check if the UserID/Phone matches the Email in DB"""
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "SELECT user_id FROM users WHERE (user_id = %s OR phone_number = %s) AND email = %s"
            cursor.execute(query, (identifier, identifier, email))
            result = cursor.fetchone()
            conn.close()
            return True if result else False
        except:
            conn.close()
            return False
    return False

def update_password(identifier, new_password):
    conn = get_connection()
    if conn:
        cursor = conn.cursor()
        try:
            query = "UPDATE users SET password = %s WHERE user_id = %s OR phone_number = %s"
            cursor.execute(query, (new_password, identifier, identifier))
            conn.commit()
            conn.close()
            return True
        except:
            conn.close()
            return False
    return False

# --- 3. MAIN UI ---
def login_page():
    st.title("Car Rental🚗")

    # Initialize Session States
    if 'auth_mode' not in st.session_state: st.session_state['auth_mode'] = 'Login'
    if 'login_attempts' not in st.session_state: st.session_state['login_attempts'] = 0
    if 'reset_verified' not in st.session_state: st.session_state['reset_verified'] = False

    # Toggle Logic
    options = ["Login", "Sign Up"]
    idx = 0 if st.session_state['auth_mode'] == 'Login' else 1
    choice = st.radio(" ", options, index=idx, horizontal=True, label_visibility="collapsed")
    st.session_state['auth_mode'] = choice

    # --- LOGIN VIEW ---
    if st.session_state['auth_mode'] == "Login":
        st.subheader("Login")
        
        with st.form("login_form"):
            # UPDATED LABEL
            identifier = st.text_input("User ID or Mobile Number")
            password = st.text_input("Password", type="password")
            submit = st.form_submit_button("Login")
            
            if submit:
                if identifier and password:
                    with st.spinner("Authenticating..."):
                        time.sleep(1)
                        is_valid, role, f_name, real_id, message = login_user(identifier, password)
                    
                    if is_valid:
                        # SUCCESS: Reset attempts
                        st.session_state['login_attempts'] = 0
                        st.session_state['logged_in'] = True
                        st.session_state['user_id'] = real_id # Save the real ID (in case they used phone)
                        st.session_state['role'] = role
                        st.session_state['user_name'] = f_name
                        st.success(message)
                        time.sleep(0.5)
                        st.rerun()
                    else:
                        # FAILURE: Increment attempts
                        st.session_state['login_attempts'] += 1
                        st.error(message)
                else:
                    st.warning("⚠️ Please fill in all fields.")

        # --- FORGOT PASSWORD SECTION (Appears after 3 fails) ---
        if st.session_state['login_attempts'] >= 3:
            st.warning(f"⚠️ Failed Attempts: {st.session_state['login_attempts']}")
            
            with st.expander("🔑 Forgot Password?", expanded=True):
                st.info("Please verify your identity to reset your password.")
                
                # Step 1: Verification
                if not st.session_state['reset_verified']:
                    check_id = st.text_input("Enter User ID or Mobile", key="fp_id")
                    check_email = st.text_input("Enter Registered Email", key="fp_email")
                    
                    if st.button("Verify Identity"):
                        if verify_reset_details(check_id, check_email):
                            st.session_state['reset_verified'] = True
                            st.session_state['reset_id'] = check_id
                            st.success("✅ Identity Verified! Set new password below.")
                            st.rerun()
                        else:
                            st.error("❌ Details do not match our records.")
                
                # Step 2: Reset Password
                else:
                    st.write(f"Resetting password for: **{st.session_state['reset_id']}**")
                    new_pass = st.text_input("New Password", type="password", key="new_p")
                    confirm_pass = st.text_input("Confirm Password", type="password", key="conf_p")
                    
                    if st.button("Update Password"):
                        if new_pass == confirm_pass and new_pass:
                            if update_password(st.session_state['reset_id'], new_pass):
                                st.success("🎉 Password Updated! Please Login.")
                                # Cleanup
                                st.session_state['login_attempts'] = 0
                                st.session_state['reset_verified'] = False
                                time.sleep(1.5)
                                st.rerun()
                            else:
                                st.error("Database Error.")
                        else:
                            st.warning("Passwords do not match or empty.")

    # --- SIGN UP VIEW ---
    elif st.session_state['auth_mode'] == "Sign Up":
        st.subheader("Create Account")
        with st.form("signup_form"):
            c1, c2 = st.columns(2)
            with c1:
                first_name = st.text_input("First Name")
                user_id = st.text_input("Choose User ID")
                email = st.text_input("Email")
            with c2:
                last_name = st.text_input("Last Name")
                phone = st.text_input("Phone Number")
                password = st.text_input("Password", type="password")
            
            submit = st.form_submit_button("Sign Up")
            
            if submit:
                if not (first_name and last_name and user_id and email and phone and password):
                    st.warning("⚠️ All fields are required.")
                else:
                    valid, val_msg = validate_inputs(email, phone)
                    if not valid:
                        st.warning(val_msg)
                    else:
                        with st.spinner("Creating account..."):
                            time.sleep(1.5)
                            is_created, db_msg = create_user(user_id, first_name, last_name, email, phone, password)
                        
                        if is_created:
                            st.success(db_msg)
                            time.sleep(1)
                            st.session_state['auth_mode'] = 'Login'
                            st.rerun()
                        else:
                            st.error(db_msg)