import streamlit as st

st.set_page_config(
    page_title="Business Database",
    layout="wide"
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
    st.write("Customer database will appear here.")

elif page == "Suppliers":
    st.header("Suppliers")
    st.write("Supplier database will appear here.")
