import streamlit as st
import time
import random

# ✅ FIXED: Now accepts 'user_info' as the second argument
def render_payment_gateway(total_amount, user_info=None):
    
    # Safety check: If no user info is passed, make it an empty dict
    if user_info is None:
        user_info = {'name': '', 'email': '', 'phone': ''}

    st.markdown("## 🔒 Secure Checkout")
    st.info(f"**Total Payable:** ₹{total_amount:,.2f}")

    # --- SECTION 1: CUSTOMER DETAILS ---
    st.markdown("#### 1. Customer Information")
    c1, c2 = st.columns(2)
    with c1:
        # ✅ We use 'value=' to auto-fill the Name and Email
        full_name = st.text_input("Full Name", value=user_info.get('name', ''), placeholder="e.g. Rahul Sharma")
        email = st.text_input("Email", value=user_info.get('email', ''), placeholder="rahul@example.com")
    with c2:
        # ✅ Auto-fill Phone
        phone = st.text_input("Phone Number", value=user_info.get('phone', ''), placeholder="9876543210", max_chars=10)
    
    st.divider()

    # --- SECTION 2: PAYMENT METHOD ---
    st.markdown("#### 2. Select Payment Method")
    method = st.radio("Choose Method", ["Credit/Debit Card", "UPI / QR", "Net Banking"], horizontal=True, label_visibility="collapsed")

    # CASE A: CREDIT/DEBIT CARD
    if method == "Credit/Debit Card":
        with st.container(border=True):
            col_c1, col_c2 = st.columns([3, 1])
            with col_c1:
                card_num = st.text_input("Card Number *", placeholder="0000 0000 0000 0000", max_chars=16)
            with col_c2:
                cvv = st.text_input("CVV *", type="password", placeholder="123", max_chars=3)
            
            col_c3, col_c4 = st.columns(2)
            with col_c3:
                from datetime import date
                expiry_date = st.date_input("Expiry Date (Month/Year) *", 
                    value=None,
                    min_value=date(2026, 2, 1),
                    max_value=date(2040, 12, 31),
                    format="MM/YYYY")
            with col_c4:
                card_holder = st.text_input("Name on Card *", placeholder="RAHUL SHARMA")

            if st.button(f"Pay ₹{total_amount}", type="primary"):
                errors = []
                
                # Check if all fields are empty
                all_empty = (
                    (not full_name or not full_name.strip()) and
                    (not email or not email.strip()) and
                    (not phone or not phone.strip()) and
                    (not card_num or not card_num.strip()) and
                    (not cvv or not cvv.strip()) and
                    not expiry_date and
                    (not card_holder or not card_holder.strip())
                )
                
                if all_empty:
                    st.error("❌ It is necessary to fill all details before making payment!")
                    return None
                
                # Validate customer details
                if not full_name or not full_name.strip():
                    errors.append("⚠️ Full Name is required.")
                if not email or not email.strip():
                    errors.append("⚠️ Email is required.")
                elif "@" not in email:
                    errors.append("⚠️ Invalid Email format.")
                if not phone or not phone.strip():
                    errors.append("⚠️ Phone Number is required.")
                elif len(phone) != 10 or not phone.isdigit():
                    errors.append("⚠️ Phone number must be exactly 10 digits.")
                
                # Validate card details - ALL REQUIRED
                if not card_num or not card_num.strip():
                    errors.append("⚠️ Card Number is required.")
                elif len(card_num) != 16 or not card_num.isdigit():
                    errors.append("⚠️ Card Number must be exactly 16 digits.")
                
                if not cvv or not cvv.strip():
                    errors.append("⚠️ CVV is required.")
                elif len(cvv) != 3 or not cvv.isdigit():
                    errors.append("⚠️ CVV must be exactly 3 digits.")
                
                if not expiry_date:
                    errors.append("⚠️ Expiry Date is required.")
                
                if not card_holder or not card_holder.strip():
                    errors.append("⚠️ Name on Card is required.")
                
                if errors:
                    st.error("❌ Please fill all required fields correctly:")
                    for err in errors:
                        st.error(err)
                else:
                    return simulate_processing("Card", full_name, email, phone)

    # CASE B: UPI
    elif method == "UPI / QR":
        with st.container(border=True):
            st.write("Scan QR or Enter UPI ID")
            c_qr, c_in = st.columns([1, 2])
            with c_qr:
                st.image(f"https://api.qrserver.com/v1/create-qr-code/?size=100x100&data=PAY_RS_{total_amount}", caption="Scan to Pay")
            with c_in:
                upi_id = st.text_input("Enter UPI ID", placeholder="mobile@upi")
                st.caption("Supported: GPay, PhonePe, Paytm")

            if st.button(f"Verify & Pay ₹{total_amount}", type="primary"):
                if not full_name:
                    st.error("⚠️ Please enter your Name in Customer Info above.")
                elif "@" not in upi_id:
                    st.error("⚠️ Invalid UPI ID (must contain '@').")
                else:
                    return simulate_processing("UPI", full_name, email, phone)

    # CASE C: NET BANKING
    elif method == "Net Banking":
        with st.container(border=True):
            bank = st.selectbox("Select Your Bank", ["HDFC Bank", "SBI", "ICICI Bank", "Axis Bank", "Kotak Bank"])
            st.info(f"You will be redirected to {bank} secure login page.")
            
            if st.button(f"Proceed to {bank}", type="primary"):
                if not full_name:
                     st.error("⚠️ Please enter your Name in Customer Info above.")
                else:
                    return simulate_processing("NetBanking", full_name, email, phone)

    return None

def simulate_processing(method, name, email, phone):
    with st.status("🔐 Encrypting connection...", expanded=True) as status:
        time.sleep(1)
        st.write("📡 Contacting Bank Server...")
        time.sleep(1.5)
        st.write("💸 Processing Payment...")
        time.sleep(1.5)
        status.update(label="Payment Approved!", state="complete", expanded=False)
    
    # Return everything the main app needs to save the booking
    return {
        'status': 'success',
        'transaction_id': f"TXN_{random.randint(1000000, 9999999)}",
        'customer_name': name,
        'customer_email': email,
        'customer_phone': phone,
        'method': method
    }