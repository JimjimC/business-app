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
    ["Home", "Customers", "Suppliers", "Products"]
)

if st.sidebar.button("Log out"):
    st.session_state.authenticated = False
    st.rerun()


if page == "Home":
    st.header("Business Dashboard")

    customer_response = (
        supabase
        .table("customers")
        .select("*")
        .execute()
    )

    supplier_response = (
        supabase
        .table("suppliers")
        .select("*")
        .execute()
    )

    customers = customer_response.data
    suppliers = supplier_response.data

    active_customers = [
        customer for customer in customers
        if customer.get("status") == "Active"
    ]

    active_suppliers = [
        supplier for supplier in suppliers
        if supplier.get("status") == "Active"
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Customers",
            len(customers)
        )

        st.metric(
            "Active Customers",
            len(active_customers)
        )

    with col2:
        st.metric(
            "Suppliers",
            len(suppliers)
        )

        st.metric(
            "Active Suppliers",
            len(active_suppliers)
        )

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
    # DELETE CUSTOMER
    # -----------------------------

    if all_customers:
        with st.expander("🗑️ Delete Customer"):

            delete_id = st.selectbox(
                "Select customer to delete",
                [customer["id"] for customer in all_customers],
                format_func=lambda customer_id: next(
                    customer["company_name"]
                    for customer in all_customers
                    if customer["id"] == customer_id
                ),
                key="delete_customer_select"
            )

            delete_customer = next(
                customer
                for customer in all_customers
                if customer["id"] == delete_id
            )

            st.warning(
                f'You are about to delete: '
                f'{delete_customer["company_name"]}'
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this customer",
                key=f"confirm_delete_{delete_id}"
            )

            if st.button(
                "Delete Customer",
                key=f"delete_button_{delete_id}"
            ):
                if not confirm_delete:
                    st.error("Please confirm the deletion first.")
                else:
                    (
                        supabase
                        .table("customers")
                        .delete()
                        .eq("id", delete_id)
                        .execute()
                    )

                    st.success("Customer deleted successfully.")
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

    # -----------------------------
    # ADD NEW SUPPLIER
    # -----------------------------

    with st.expander("➕ Add New Supplier"):
        with st.form("add_supplier_form"):
            company_name = st.text_input("Company name")
            contact_person = st.text_input("Contact person")
            phone = st.text_input("Phone")
            email = st.text_input("Email")
            address = st.text_input("Address")
            category = st.text_input("Category")
            notes = st.text_area("Notes")
            status = st.selectbox(
                "Status",
                ["Active", "Inactive"]
            )

            submitted = st.form_submit_button("Save Supplier")

            if submitted:
                if not company_name.strip():
                    st.error("Company name is required.")
                else:
                    supabase.table("suppliers").insert({
                        "company_name": company_name,
                        "contact_person": contact_person,
                        "phone": phone,
                        "email": email,
                        "address": address,
                        "category": category,
                        "notes": notes,
                        "status": status
                    }).execute()

                    st.success("Supplier saved successfully.")
                    st.rerun()

    # -----------------------------
    # GET SUPPLIERS
    # -----------------------------

    response = (
        supabase
        .table("suppliers")
        .select("*")
        .order("id")
        .execute()
    )

    all_suppliers = response.data

    # -----------------------------
    # EDIT SUPPLIER
    # -----------------------------

    if all_suppliers:
        with st.expander("✏️ Edit Supplier"):

            supplier_ids = [
                supplier["id"]
                for supplier in all_suppliers
            ]

            selected_id = st.selectbox(
                "Select supplier",
                supplier_ids,
                format_func=lambda supplier_id: next(
                    supplier["company_name"]
                    for supplier in all_suppliers
                    if supplier["id"] == supplier_id
                )
            )

            selected_supplier = next(
                supplier
                for supplier in all_suppliers
                if supplier["id"] == selected_id
            )

            with st.form("edit_supplier_form"):

                edit_company_name = st.text_input(
                    "Company name",
                    value=selected_supplier.get("company_name") or "",
                    key=f"edit_supplier_company_{selected_id}"
                )

                edit_contact_person = st.text_input(
                    "Contact person",
                    value=selected_supplier.get("contact_person") or "",
                    key=f"edit_supplier_contact_{selected_id}"
                )

                edit_phone = st.text_input(
                    "Phone",
                    value=selected_supplier.get("phone") or "",
                    key=f"edit_supplier_phone_{selected_id}"
                )

                edit_email = st.text_input(
                    "Email",
                    value=selected_supplier.get("email") or "",
                    key=f"edit_supplier_email_{selected_id}"
                )

                edit_address = st.text_input(
                    "Address",
                    value=selected_supplier.get("address") or "",
                    key=f"edit_supplier_address_{selected_id}"
                )

                edit_category = st.text_input(
                    "Category",
                    value=selected_supplier.get("category") or "",
                    key=f"edit_supplier_category_{selected_id}"
                )

                edit_notes = st.text_area(
                    "Notes",
                    value=selected_supplier.get("notes") or "",
                    key=f"edit_supplier_notes_{selected_id}"
                )

                current_status = selected_supplier.get("status") or "Active"

                edit_status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if current_status == "Active" else 1,
                    key=f"edit_supplier_status_{selected_id}"
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
                            .table("suppliers")
                            .update({
                                "company_name": edit_company_name,
                                "contact_person": edit_contact_person,
                                "phone": edit_phone,
                                "email": edit_email,
                                "address": edit_address,
                                "category": edit_category,
                                "notes": edit_notes,
                                "status": edit_status
                            })
                            .eq("id", selected_id)
                            .execute()
                        )

                        st.success("Supplier updated successfully.")
                        st.rerun()
    # -----------------------------
    # DELETE SUPPLIER
    # -----------------------------

    if all_suppliers:
        with st.expander("🗑️ Delete Supplier"):

            delete_id = st.selectbox(
                "Select supplier to delete",
                [supplier["id"] for supplier in all_suppliers],
                format_func=lambda supplier_id: next(
                    supplier["company_name"]
                    for supplier in all_suppliers
                    if supplier["id"] == supplier_id
                ),
                key="delete_supplier_select"
            )

            delete_supplier = next(
                supplier
                for supplier in all_suppliers
                if supplier["id"] == delete_id
            )

            st.warning(
                f'You are about to delete: '
                f'{delete_supplier["company_name"]}'
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this supplier",
                key=f"confirm_supplier_delete_{delete_id}"
            )

            if st.button(
                "Delete Supplier",
                key=f"delete_supplier_button_{delete_id}"
            ):
                if not confirm_delete:
                    st.error("Please confirm the deletion first.")
                else:
                    (
                        supabase
                        .table("suppliers")
                        .delete()
                        .eq("id", delete_id)
                        .execute()
                    )

                    st.success("Supplier deleted successfully.")
                    st.rerun()
    # -----------------------------
    # SEARCH SUPPLIERS
    # -----------------------------

    suppliers = all_suppliers

    search = st.text_input(
        "🔎 Search suppliers",
        placeholder="Search by company, contact, phone, email or category"
    )

    if search:
        search_lower = search.lower()

        suppliers = [
            supplier for supplier in suppliers
            if search_lower in str(supplier.get("company_name", "")).lower()
            or search_lower in str(supplier.get("contact_person", "")).lower()
            or search_lower in str(supplier.get("phone", "")).lower()
            or search_lower in str(supplier.get("email", "")).lower()
            or search_lower in str(supplier.get("category", "")).lower()
        ]

    # -----------------------------
    # DISPLAY SUPPLIERS
    # -----------------------------

    if suppliers:
        st.dataframe(
            suppliers,
            use_container_width=True
        )
    else:
        st.info("No suppliers found.")

elif page == "Products":
    st.header("Products")

    # -----------------------------
    # GET SUPPLIERS
    # -----------------------------

    supplier_response = (
        supabase
        .table("suppliers")
        .select("id, company_name")
        .order("company_name")
        .execute()
    )

    supplier_list = supplier_response.data

    supplier_names = {
        supplier["id"]: supplier["company_name"]
        for supplier in supplier_list
    }

    # -----------------------------
    # ADD NEW PRODUCT
    # -----------------------------

    with st.expander("➕ Add New Product"):

        if not supplier_list:
            st.warning("You need at least one supplier before adding products.")

        else:
            with st.form("add_product_form"):
                product_name = st.text_input("Product name")
                product_code = st.text_input("Product code")

                supplier_id = st.selectbox(
                    "Supplier",
                    [supplier["id"] for supplier in supplier_list],
                    format_func=lambda supplier_id: supplier_names[supplier_id]
                )

                category = st.text_input("Category")
                unit = st.text_input(
                    "Unit",
                    placeholder="Example: bottle, carton, kg"
                )

                cost_price = st.number_input(
                    "Cost price",
                    min_value=0.0,
                    step=0.01
                )

                selling_price = st.number_input(
                    "Selling price",
                    min_value=0.0,
                    step=0.01
                )

                stock_quantity = st.number_input(
                    "Stock quantity",
                    min_value=0.0,
                    step=1.0
                )

                notes = st.text_area("Notes")

                status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"]
                )

                submitted = st.form_submit_button("Save Product")

                if submitted:
                    if not product_name.strip():
                        st.error("Product name is required.")
                    else:
                        supabase.table("products").insert({
                            "product_name": product_name,
                            "product_code": product_code,
                            "supplier_id": supplier_id,
                            "category": category,
                            "unit": unit,
                            "cost_price": cost_price,
                            "selling_price": selling_price,
                            "stock_quantity": stock_quantity,
                            "notes": notes,
                            "status": status
                        }).execute()

                        st.success("Product saved successfully.")
                        st.rerun()

    # -----------------------------
    # GET PRODUCTS
    # -----------------------------

    product_response = (
        supabase
        .table("products")
        .select("*")
        .order("id")
        .execute()
    )

    products = product_response.data

    # Replace supplier ID with supplier name for display
    display_products = []

    for product in products:
        product_copy = product.copy()

        product_copy["supplier"] = supplier_names.get(
            product.get("supplier_id"),
            "Unknown"
        )

        display_products.append(product_copy)

    # -----------------------------
    # SEARCH PRODUCTS
    # -----------------------------

    search = st.text_input(
        "🔎 Search products",
        placeholder="Search by product, code, supplier or category"
    )

    if search:
        search_lower = search.lower()

        display_products = [
            product for product in display_products
            if search_lower in str(product.get("product_name", "")).lower()
            or search_lower in str(product.get("product_code", "")).lower()
            or search_lower in str(product.get("supplier", "")).lower()
            or search_lower in str(product.get("category", "")).lower()
        ]

    # -----------------------------
    # DISPLAY PRODUCTS
    # -----------------------------

    if display_products:
        st.dataframe(
            display_products,
            use_container_width=True
        )
    else:
        st.info("No products found.")
