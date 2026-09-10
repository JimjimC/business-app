import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Business Database",
    layout="wide"
)

# -----------------------------
# LOGIN
# -----------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("Business Database App")

    password = st.text_input(
        "Enter password",
        type="password"
    )

    if st.button("Log in"):
        if password == st.secrets["APP_PASSWORD"]:
            st.session_state.authenticated = True
            st.rerun()
        else:
            st.error("Incorrect password")

    st.stop()


# -----------------------------
# CONNECT TO SUPABASE
# -----------------------------

supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)


# -----------------------------
# MAIN APP
# -----------------------------

st.title("Business Database App")

page = st.sidebar.radio(
    "Menu",
    ["Home", "Customers", "Suppliers"]
)

if st.sidebar.button("Log out"):
    st.session_state.authenticated = False
    st.rerun()


if page == "Home":
    st.header("Home")
    st.write("Welcome to the Business Database.")

elif page == "Customers":
    st.header("Customers")

    # -----------------------------
    # ADD NEW CUSTOMER
    # -----------------------------

    with st.expander("➕ Add New Customer"):
        with st.form("add_customer_form"):
            company_name = st.text_input("Company name")
            contact_person = st.text_input("Contact person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_input("Address")
            notes = st.text_area("Notes")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"]
            )

            submitted = st.form_submit_button("Save Customer")

            if submitted:
                if not company_name.strip():
                    st.error("Company name is required.")
                else:
                    supabase.table("customers").insert({
                        "company_name": company_name,
                        "contact_person": contact_person,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "notes": notes,
                        "status": status
                    }).execute()

                    st.success("Customer saved successfully.")
                    st.rerun()

    # -----------------------------
    # GET CUSTOMERS
    # -----------------------------

    response = (
        supabase
        .table("customers")
        .select("*")
        .order("id")
        .execute()
    )

    all_customers = response.data

    # -----------------------------
    # EDIT CUSTOMER
    # -----------------------------

    if all_customers:
        with st.expander("✏️ Edit Customer"):

            customer_ids = [
                customer["id"]
                for customer in all_customers
            ]

            selected_id = st.selectbox(
                "Select customer",
                customer_ids,
                format_func=lambda customer_id: next(
                    customer["company_name"]
                    for customer in all_customers
                    if customer["id"] == customer_id
                )
            )

            selected_customer = next(
                customer
                for customer in all_customers
                if customer["id"] == selected_id
            )

            with st.form("edit_customer_form"):

                edit_company_name = st.text_input(
                    "Company name",
                    value=selected_customer.get("company_name") or "",
                    key=f"edit_company_{selected_id}"
                )

                edit_contact_person = st.text_input(
                    "Contact person",
                    value=selected_customer.get("contact_person") or "",
                    key=f"edit_contact_{selected_id}"
                )

                edit_phone = st.text_input(
                    "Phone",
                    value=selected_customer.get("phone") or "",
                    key=f"edit_phone_{selected_id}"
                )

                edit_email = st.text_input(
                    "Email",
                    value=selected_customer.get("email") or "",
                    key=f"edit_email_{selected_id}"
                )

                edit_address = st.text_input(
                    "Address",
                    value=selected_customer.get("address") or "",
                    key=f"edit_address_{selected_id}"
                )

                edit_notes = st.text_area(
                    "Notes",
                    value=selected_customer.get("notes") or "",
                    key=f"edit_notes_{selected_id}"
                )

                current_status = selected_customer.get("status") or "Active"

                edit_status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if current_status == "Active" else 1,
                    key=f"edit_status_{selected_id}"
                )

                update_submitted = st.form_submit_button(
                    "Save Changes"
                )

                if update_submitted:
                    if not edit_company_name.strip():
                        st.error("Company name is required.")
                    else:
                        (
                            supabase
                            .table("customers")
                            .update({
                                "company_name": edit_company_name,
                                "contact_person": edit_contact_person,
                                "phone": edit_phone,
                                "email": edit_email,
                                "address": edit_address,
                                "notes": edit_notes,
                                "status": edit_status
                            })
                            .eq("id", selected_id)
                            .execute()
                        )

                        st.success("Customer updated successfully.")
                        st.rerun()

    # -----------------------------
    # SEARCH CUSTOMERS
    # -----------------------------

    customers = all_customers

    search = st.text_input(
        "🔎 Search customers",
        placeholder="Search by company, contact, phone or email"
    )

    if search:
        search_lower = search.lower()

        customers = [
            customer for customer in customers
            if search_lower in str(customer.get("company_name", "")).lower()
            or search_lower in str(customer.get("contact_person", "")).lower()
            or search_lower in str(customer.get("phone", "")).lower()
            or search_lower in str(customer.get("email", "")).lower()
        ]

    # -----------------------------
    # DISPLAY CUSTOMERS
    # -----------------------------

    if customers:
        st.dataframe(
            customers,
            use_container_width=True
        )
    else:
        st.info("No customers found.")


elif page == "Suppliers":
    st.header("Suppliers")
    st.write("Supplier database will appear here.")


elif page == "Suppliers":
    st.header("Suppliers")
    st.write("Supplier database will appear here.")
