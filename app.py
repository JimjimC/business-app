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

    response = supabase.table("customers").select("*").execute()
    customers = response.data

    if customers:
        st.dataframe(customers, use_container_width=True)
    else:
        st.info("No customers found.")

elif page == "Suppliers":
    st.header("Suppliers")
    st.write("Supplier database will appear here.")
