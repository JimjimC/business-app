import streamlit as st
from supabase import create_client

st.set_page_config(
    page_title="Business Database",
    layout="wide"
)

# Connect to Supabase
supabase = create_client(
    st.secrets["SUPABASE_URL"],
    st.secrets["SUPABASE_KEY"]
)

st.title("Business Database App")

page = st.sidebar.radio(
    "Menu",
    ["Home", "Customers", "Suppliers"]
)

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
