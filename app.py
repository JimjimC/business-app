import streamlit as st
from supabase import create_client
from datetime import date

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
    ["Home", "Customers", "Suppliers", "Products", "Invoices", "Payments"]
)

if st.sidebar.button("Log out"):
    st.session_state.authenticated = False
    st.rerun()


if page == "Home":
    st.header("Business Dashboard")

    # -----------------------------
    # GET DATA
    # -----------------------------

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

    invoice_response = (
        supabase
        .table("invoices")
        .select("*")
        .execute()
    )

    payment_response = (
        supabase
        .table("payments")
        .select("*")
        .execute()
    )

    customers = customer_response.data
    suppliers = supplier_response.data
    invoices = invoice_response.data
    payments = payment_response.data

    # -----------------------------
    # BASIC COUNTS
    # -----------------------------

    active_customers = [
        customer for customer in customers
        if customer.get("status") == "Active"
    ]

    active_suppliers = [
        supplier for supplier in suppliers
        if supplier.get("status") == "Active"
    ]

    # -----------------------------
    # PAYMENT TOTALS
    # -----------------------------

    total_payments_received = sum(
        float(payment.get("amount") or 0)
        for payment in payments
    )

    payments_by_invoice = {}

    for payment in payments:
        invoice_id = payment["invoice_id"]

        payments_by_invoice[invoice_id] = (
            payments_by_invoice.get(invoice_id, 0)
            + float(payment.get("amount") or 0)
        )

    # -----------------------------
    # OUTSTANDING + OVERDUE INVOICES
    # -----------------------------

    customer_names = {
        customer["id"]: customer["company_name"]
        for customer in customers
    }

    outstanding_amount = 0
    outstanding_count = 0

    overdue_amount = 0
    overdue_invoices = []

    today = date.today()

    for invoice in invoices:

        if invoice.get("status") == "Cancelled":
            continue

        invoice_total = float(
            invoice.get("total_amount") or 0
        )

        amount_paid = payments_by_invoice.get(
            invoice["id"],
            0
        )

        balance = invoice_total - amount_paid

        if balance > 0.01:

            outstanding_count += 1
            outstanding_amount += balance

            due_date_value = invoice.get("due_date")

            if due_date_value:

                invoice_due_date = date.fromisoformat(
                    due_date_value
                )

                if invoice_due_date < today:

                    overdue_amount += balance

                    overdue_invoices.append({
                        "Invoice": invoice["invoice_number"],
                        "Customer": customer_names.get(
                            invoice["customer_id"],
                            "Unknown"
                        ),
                        "Due Date": due_date_value,
                        "Balance": round(balance, 2)
                    })

    overdue_count = len(overdue_invoices)

    paid_invoices = [
        invoice for invoice in invoices
        if invoice.get("status") == "Paid"
    ]
    # -----------------------------
    # DASHBOARD
    # -----------------------------

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Customers",
            len(customers)
        )

    with col2:
        st.metric(
            "Suppliers",
            len(suppliers)
        )

    with col3:
        st.metric(
            "Invoices",
            len(invoices)
        )

    with col4:
        st.metric(
            "Paid Invoices",
            len(paid_invoices)
        )

    st.divider()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Active Customers",
            len(active_customers)
        )

    with col2:
        st.metric(
            "Active Suppliers",
            len(active_suppliers)
        )

    with col3:
        st.metric(
            "Outstanding Invoices",
            outstanding_count
        )

    with col4:
        st.metric(
            "Outstanding Amount",
            f"{outstanding_amount:,.2f}"
        )

    st.divider()

    st.metric(
        "Total Payments Received",
        f"{total_payments_received:,.2f}"
    )

    st.divider()

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Overdue Invoices",
            overdue_count
        )

    with col2:
        st.metric(
            "Overdue Amount",
            f"{overdue_amount:,.2f}"
        )

    st.subheader("Overdue Invoice Details")

    if overdue_invoices:
        st.dataframe(
            overdue_invoices,
            use_container_width=True
        )
    else:
        st.success("No overdue invoices.")


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
    # EDIT PRODUCT
    # -----------------------------

    if products:
        with st.expander("✏️ Edit Product"):

            product_ids = [
                product["id"]
                for product in products
            ]

            selected_id = st.selectbox(
                "Select product",
                product_ids,
                format_func=lambda product_id: next(
                    product["product_name"]
                    for product in products
                    if product["id"] == product_id
                )
            )

            selected_product = next(
                product
                for product in products
                if product["id"] == selected_id
            )

            current_supplier_id = selected_product.get("supplier_id")

            supplier_ids = [
                supplier["id"]
                for supplier in supplier_list
            ]

            if current_supplier_id in supplier_ids:
                supplier_index = supplier_ids.index(current_supplier_id)
            else:
                supplier_index = 0

            with st.form("edit_product_form"):

                edit_product_name = st.text_input(
                    "Product name",
                    value=selected_product.get("product_name") or "",
                    key=f"edit_product_name_{selected_id}"
                )

                edit_product_code = st.text_input(
                    "Product code",
                    value=selected_product.get("product_code") or "",
                    key=f"edit_product_code_{selected_id}"
                )

                edit_supplier_id = st.selectbox(
                    "Supplier",
                    supplier_ids,
                    index=supplier_index,
                    format_func=lambda supplier_id: supplier_names[supplier_id],
                    key=f"edit_product_supplier_{selected_id}"
                )

                edit_category = st.text_input(
                    "Category",
                    value=selected_product.get("category") or "",
                    key=f"edit_product_category_{selected_id}"
                )

                edit_unit = st.text_input(
                    "Unit",
                    value=selected_product.get("unit") or "",
                    key=f"edit_product_unit_{selected_id}"
                )

                edit_cost_price = st.number_input(
                    "Cost price",
                    min_value=0.0,
                    value=float(selected_product.get("cost_price") or 0),
                    step=0.01,
                    key=f"edit_product_cost_{selected_id}"
                )

                edit_selling_price = st.number_input(
                    "Selling price",
                    min_value=0.0,
                    value=float(selected_product.get("selling_price") or 0),
                    step=0.01,
                    key=f"edit_product_selling_{selected_id}"
                )

                edit_stock_quantity = st.number_input(
                    "Stock quantity",
                    min_value=0.0,
                    value=float(selected_product.get("stock_quantity") or 0),
                    step=1.0,
                    key=f"edit_product_stock_{selected_id}"
                )

                edit_notes = st.text_area(
                    "Notes",
                    value=selected_product.get("notes") or "",
                    key=f"edit_product_notes_{selected_id}"
                )

                current_status = selected_product.get("status") or "Active"

                edit_status = st.selectbox(
                    "Status",
                    ["Active", "Inactive"],
                    index=0 if current_status == "Active" else 1,
                    key=f"edit_product_status_{selected_id}"
                )

                update_submitted = st.form_submit_button(
                    "Save Changes"
                )

                if update_submitted:
                    if not edit_product_name.strip():
                        st.error("Product name is required.")
                    else:
                        (
                            supabase
                            .table("products")
                            .update({
                                "product_name": edit_product_name,
                                "product_code": edit_product_code,
                                "supplier_id": edit_supplier_id,
                                "category": edit_category,
                                "unit": edit_unit,
                                "cost_price": edit_cost_price,
                                "selling_price": edit_selling_price,
                                "stock_quantity": edit_stock_quantity,
                                "notes": edit_notes,
                                "status": edit_status
                            })
                            .eq("id", selected_id)
                            .execute()
                        )

                        st.success("Product updated successfully.")
                        st.rerun()
                            
    # -----------------------------
    # DELETE PRODUCT
    # -----------------------------

    if products:
        with st.expander("🗑️ Delete Product"):

            delete_id = st.selectbox(
                "Select product to delete",
                [product["id"] for product in products],
                format_func=lambda product_id: next(
                    product["product_name"]
                    for product in products
                    if product["id"] == product_id
                ),
                key="delete_product_select"
            )

            delete_product = next(
                product
                for product in products
                if product["id"] == delete_id
            )

            st.warning(
                f'You are about to delete: '
                f'{delete_product["product_name"]}'
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this product",
                key=f"confirm_product_delete_{delete_id}"
            )

            if st.button(
                "Delete Product",
                key=f"delete_product_button_{delete_id}"
            ):
                if not confirm_delete:
                    st.error("Please confirm the deletion first.")
                else:
                    (
                        supabase
                        .table("products")
                        .delete()
                        .eq("id", delete_id)
                        .execute()
                    )

                    st.success("Product deleted successfully.")
                    st.rerun()
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
if page == "Invoices":
    st.header("Invoices")

    # -----------------------------
    # GET CUSTOMERS
    # -----------------------------

    customer_response = (
        supabase
        .table("customers")
        .select("id, company_name")
        .order("company_name")
        .execute()
    )

    customer_list = customer_response.data

    customer_names = {
        customer["id"]: customer["company_name"]
        for customer in customer_list
    }

    # -----------------------------
    # CREATE INVOICE
    # -----------------------------

    with st.expander("➕ Create Invoice"):

        if not customer_list:
            st.warning("You need at least one customer before creating an invoice.")

        else:
            with st.form("create_invoice_form"):

                invoice_number = st.text_input(
                    "Invoice number",
                    placeholder="Example: INV-1001"
                )

                customer_id = st.selectbox(
                    "Customer",
                    [customer["id"] for customer in customer_list],
                    format_func=lambda customer_id: customer_names[customer_id]
                )

                invoice_date = st.date_input(
                    "Invoice date",
                    value=date.today()
                )

                due_date = st.date_input(
                    "Due date",
                    value=date.today()
                )

                status = st.selectbox(
                    "Status",
                    ["Draft", "Unpaid"]
                )

                notes = st.text_area("Notes")

                submitted = st.form_submit_button("Create Invoice")

                if submitted:
                    if not invoice_number.strip():
                        st.error("Invoice number is required.")
                    else:
                        supabase.table("invoices").insert({
                            "invoice_number": invoice_number,
                            "customer_id": customer_id,
                            "invoice_date": str(invoice_date),
                            "due_date": str(due_date),
                            "status": status,
                            "subtotal": 0,
                            "tax_amount": 0,
                            "total_amount": 0,
                            "notes": notes
                        }).execute()

                        st.success("Invoice created successfully.")
                        st.rerun()

    # -----------------------------
    # GET INVOICES
    # -----------------------------

    invoice_response = (
        supabase
        .table("invoices")
        .select("*")
        .order("id")
        .execute()
    )

    invoices = invoice_response.data
    
    # -----------------------------
    # ADD PRODUCT LINE
    # -----------------------------

    if invoices:
        with st.expander("➕ Add Product Line"):

            # Get active products
            invoice_product_response = (
                supabase
                .table("products")
                .select("id, product_name, selling_price")
                .eq("status", "Active")
                .order("product_name")
                .execute()
            )

            invoice_products = invoice_product_response.data

            if not invoice_products:
                st.warning("You need at least one active product.")

            else:
                # Select invoice
                selected_invoice_id = st.selectbox(
                    "Invoice",
                    [invoice["id"] for invoice in invoices],
                    format_func=lambda invoice_id: next(
                        f'{invoice["invoice_number"]} - '
                        f'{customer_names.get(invoice["customer_id"], "Unknown")}'
                        for invoice in invoices
                        if invoice["id"] == invoice_id
                    )
                )

                # Select product
                selected_product_id = st.selectbox(
                    "Product",
                    [product["id"] for product in invoice_products],
                    format_func=lambda product_id: next(
                        product["product_name"]
                        for product in invoice_products
                        if product["id"] == product_id
                    )
                )

                selected_product = next(
                    product
                    for product in invoice_products
                    if product["id"] == selected_product_id
                )

                quantity = st.number_input(
                    "Quantity",
                    min_value=0.01,
                    value=1.0,
                    step=1.0
                )

                unit_price = st.number_input(
                    "Unit price",
                    min_value=0.0,
                    value=float(
                        selected_product.get("selling_price") or 0
                    ),
                    step=0.01
                )

                line_total = round(quantity * unit_price, 2)

                st.write(
                    f"**Line total: {line_total:.2f}**"
                )

                if st.button("Add Product to Invoice"):

                    # Save invoice line
                    supabase.table("invoice_items").insert({
                        "invoice_id": selected_invoice_id,
                        "product_id": selected_product_id,
                        "description": selected_product["product_name"],
                        "quantity": quantity,
                        "unit_price": unit_price,
                        "line_total": line_total
                    }).execute()

                    # Get all lines for this invoice
                    items_response = (
                        supabase
                        .table("invoice_items")
                        .select("line_total")
                        .eq("invoice_id", selected_invoice_id)
                        .execute()
                    )

                    items = items_response.data

                    subtotal = sum(
                        float(item.get("line_total") or 0)
                        for item in items
                    )

                    tax_amount = 0
                    total_amount = subtotal + tax_amount

                    # Update invoice totals
                    (
                        supabase
                        .table("invoices")
                        .update({
                            "subtotal": subtotal,
                            "tax_amount": tax_amount,
                            "total_amount": total_amount
                        })
                        .eq("id", selected_invoice_id)
                        .execute()
                    )

                    st.success("Product added to invoice.")
                    st.rerun()
    # -----------------------------
    # VIEW INVOICE DETAILS
    # -----------------------------

    if invoices:
        with st.expander("📄 View Invoice Details"):

            view_invoice_id = st.selectbox(
                "Select invoice to view",
                [invoice["id"] for invoice in invoices],
                format_func=lambda invoice_id: next(
                    f'{invoice["invoice_number"]} - '
                    f'{customer_names.get(invoice["customer_id"], "Unknown")}'
                    for invoice in invoices
                    if invoice["id"] == invoice_id
                ),
                key="view_invoice_select"
            )

            selected_invoice = next(
                invoice
                for invoice in invoices
                if invoice["id"] == view_invoice_id
            )

            st.write(
                f'**Customer:** '
                f'{customer_names.get(selected_invoice["customer_id"], "Unknown")}'
            )

            st.write(
                f'**Invoice number:** '
                f'{selected_invoice["invoice_number"]}'
            )

            st.write(
                f'**Invoice date:** '
                f'{selected_invoice["invoice_date"]}'
            )

            st.write(
                f'**Due date:** '
                f'{selected_invoice["due_date"]}'
            )

            # Get invoice product lines
            item_response = (
                supabase
                .table("invoice_items")
                .select("*")
                .eq("invoice_id", view_invoice_id)
                .order("id")
                .execute()
            )

            invoice_items = item_response.data

            if invoice_items:
                display_items = []

                for item in invoice_items:
                    display_items.append({
                        "Product": item["description"],
                        "Quantity": item["quantity"],
                        "Unit Price": item["unit_price"],
                        "Line Total": item["line_total"]
                    })

                st.dataframe(
                    display_items,
                    use_container_width=True
                )

                col1, col2, col3 = st.columns(3)

                with col1:
                    st.metric(
                        "Subtotal",
                        f'{float(selected_invoice["subtotal"] or 0):.2f}'
                    )

                with col2:
                    st.metric(
                        "Tax",
                        f'{float(selected_invoice["tax_amount"] or 0):.2f}'
                    )

                with col3:
                    st.metric(
                        "Total",
                        f'{float(selected_invoice["total_amount"] or 0):.2f}'
                    )

            else:
                st.info("This invoice has no product lines yet.")

    # -----------------------------
    # REMOVE PRODUCT LINE
    # -----------------------------

    if invoices:
        with st.expander("🗑️ Remove Product Line"):

            remove_invoice_id = st.selectbox(
                "Select invoice",
                [invoice["id"] for invoice in invoices],
                format_func=lambda invoice_id: next(
                    f'{invoice["invoice_number"]} - '
                    f'{customer_names.get(invoice["customer_id"], "Unknown")}'
                    for invoice in invoices
                    if invoice["id"] == invoice_id
                ),
                key="remove_line_invoice"
            )

            remove_items_response = (
                supabase
                .table("invoice_items")
                .select("*")
                .eq("invoice_id", remove_invoice_id)
                .order("id")
                .execute()
            )

            remove_items = remove_items_response.data

            if remove_items:

                remove_item_id = st.selectbox(
                    "Select product line",
                    [item["id"] for item in remove_items],
                    format_func=lambda item_id: next(
                        f'{item["description"]} - '
                        f'Qty {item["quantity"]} - '
                        f'{float(item["line_total"]):.2f}'
                        for item in remove_items
                        if item["id"] == item_id
                    ),
                    key="remove_invoice_item"
                )

                selected_remove_item = next(
                    item
                    for item in remove_items
                    if item["id"] == remove_item_id
                )

                st.warning(
                    f'You are about to remove: '
                    f'{selected_remove_item["description"]}'
                )

                confirm_remove = st.checkbox(
                    "I confirm that I want to remove this product line",
                    key=f"confirm_remove_line_{remove_item_id}"
                )

                if st.button(
                    "Remove Product Line",
                    key=f"remove_line_button_{remove_item_id}"
                ):

                    if not confirm_remove:
                        st.error("Please confirm the removal first.")

                    else:
                        # Delete product line
                        (
                            supabase
                            .table("invoice_items")
                            .delete()
                            .eq("id", remove_item_id)
                            .execute()
                        )

                        # Get remaining invoice lines
                        remaining_response = (
                            supabase
                            .table("invoice_items")
                            .select("line_total")
                            .eq("invoice_id", remove_invoice_id)
                            .execute()
                        )

                        remaining_items = remaining_response.data

                        subtotal = sum(
                            float(item.get("line_total") or 0)
                            for item in remaining_items
                        )

                        tax_amount = 0
                        total_amount = subtotal + tax_amount

                        # Update invoice totals
                        (
                            supabase
                            .table("invoices")
                            .update({
                                "subtotal": subtotal,
                                "tax_amount": tax_amount,
                                "total_amount": total_amount
                            })
                            .eq("id", remove_invoice_id)
                            .execute()
                        )

                        st.success("Product line removed.")
                        st.rerun()

            else:
                st.info("This invoice has no product lines.")

    # -----------------------------
    # EDIT INVOICE
    # -----------------------------

    if invoices:
        with st.expander("✏️ Edit Invoice"):

            edit_invoice_id = st.selectbox(
                "Select invoice to edit",
                [invoice["id"] for invoice in invoices],
                format_func=lambda invoice_id: next(
                    f'{invoice["invoice_number"]} - '
                    f'{customer_names.get(invoice["customer_id"], "Unknown")}'
                    for invoice in invoices
                    if invoice["id"] == invoice_id
                ),
                key="edit_invoice_select"
            )

            selected_edit_invoice = next(
                invoice
                for invoice in invoices
                if invoice["id"] == edit_invoice_id
            )

            customer_ids = [
                customer["id"]
                for customer in customer_list
            ]

            current_customer_id = selected_edit_invoice["customer_id"]

            if current_customer_id in customer_ids:
                customer_index = customer_ids.index(current_customer_id)
            else:
                customer_index = 0

            with st.form("edit_invoice_form"):

                edit_invoice_number = st.text_input(
                    "Invoice number",
                    value=selected_edit_invoice.get("invoice_number") or ""
                )

                edit_customer_id = st.selectbox(
                    "Customer",
                    customer_ids,
                    index=customer_index,
                    format_func=lambda customer_id: customer_names[customer_id]
                )

                edit_invoice_date = st.date_input(
                    "Invoice date",
                    value=date.fromisoformat(
                        selected_edit_invoice["invoice_date"]
                    )
                )

                edit_due_date = st.date_input(
                    "Due date",
                    value=date.fromisoformat(
                        selected_edit_invoice["due_date"]
                    )
                )

                current_status = (
                    selected_edit_invoice.get("status") or "Draft"
                )

                if current_status == "Paid":
                    edit_status = st.selectbox(
                        "Status",
                        ["Paid"],
                        disabled=True
                    )

                    st.info(
                        "This invoice is Paid because its balance is zero. "
                        "Payment records control this status."
                    )

                else:
                    status_options = [
                        "Draft",
                        "Unpaid",
                        "Cancelled"
                    ]

                    status_index = (
                        status_options.index(current_status)
                        if current_status in status_options
                        else 0
                    )

                    edit_status = st.selectbox(
                        "Status",
                        status_options,
                        index=status_index
                    )

                edit_notes = st.text_area(
                    "Notes",
                    value=selected_edit_invoice.get("notes") or ""
                )

                update_invoice = st.form_submit_button(
                    "Save Invoice Changes"
                )

                if update_invoice:

                    if not edit_invoice_number.strip():
                        st.error("Invoice number is required.")

                    else:
                        (
                            supabase
                            .table("invoices")
                            .update({
                                "invoice_number": edit_invoice_number,
                                "customer_id": edit_customer_id,
                                "invoice_date": str(edit_invoice_date),
                                "due_date": str(edit_due_date),
                                "status": edit_status,
                                "notes": edit_notes
                            })
                            .eq("id", edit_invoice_id)
                            .execute()
                        )

                        st.success("Invoice updated successfully.")
                        st.rerun()

   
    # -----------------------------
    # DELETE INVOICE
    # -----------------------------

    if invoices:
        with st.expander("🗑️ Delete Invoice"):

            delete_invoice_id = st.selectbox(
                "Select invoice to delete",
                [invoice["id"] for invoice in invoices],
                format_func=lambda invoice_id: next(
                    f'{invoice["invoice_number"]} - '
                    f'{customer_names.get(invoice["customer_id"], "Unknown")}'
                    for invoice in invoices
                    if invoice["id"] == invoice_id
                ),
                key="delete_invoice_select"
            )

            delete_invoice = next(
                invoice
                for invoice in invoices
                if invoice["id"] == delete_invoice_id
            )

            st.warning(
                f'You are about to permanently delete '
                f'{delete_invoice["invoice_number"]}.'
            )

            confirm_delete = st.checkbox(
                "I confirm that I want to delete this invoice",
                key=f"confirm_invoice_delete_{delete_invoice_id}"
            )

            if st.button(
                "Delete Invoice",
                key=f"delete_invoice_button_{delete_invoice_id}"
            ):

                if not confirm_delete:
                    st.error("Please confirm the deletion first.")

                else:
                    # Delete invoice product lines first
                    (
                        supabase
                        .table("invoice_items")
                        .delete()
                        .eq("invoice_id", delete_invoice_id)
                        .execute()
                    )

                    # Delete invoice
                    (
                        supabase
                        .table("invoices")
                        .delete()
                        .eq("id", delete_invoice_id)
                        .execute()
                    )

                    st.success("Invoice deleted successfully.")
                    st.rerun()
    # -----------------------------
    # DISPLAY INVOICES
    # -----------------------------

    display_invoices = []

    for invoice in invoices:
        invoice_copy = invoice.copy()

        invoice_copy["customer"] = customer_names.get(
            invoice.get("customer_id"),
            "Unknown"
        )

        display_invoices.append(invoice_copy)

    if display_invoices:
        st.dataframe(
            display_invoices,
            use_container_width=True
        )
    else:
        st.info("No invoices found.")

if page == "Payments":
    st.header("Payments")

    # -----------------------------
    # GET CUSTOMERS
    # -----------------------------

    payment_customer_response = (
        supabase
        .table("customers")
        .select("id, company_name")
        .execute()
    )

    payment_customers = payment_customer_response.data

    payment_customer_names = {
        customer["id"]: customer["company_name"]
        for customer in payment_customers
    }

    # -----------------------------
    # GET INVOICES
    # -----------------------------

    payment_invoice_response = (
        supabase
        .table("invoices")
        .select("*")
        .order("id")
        .execute()
    )

    payment_invoices = payment_invoice_response.data

    # -----------------------------
    # GET EXISTING PAYMENTS
    # -----------------------------

    existing_payment_response = (
        supabase
        .table("payments")
        .select("*")
        .order("id")
        .execute()
    )

    existing_payments = existing_payment_response.data

    # -----------------------------
    # CALCULATE BALANCES
    # -----------------------------

    invoice_balances = {}

    for invoice in payment_invoices:

        invoice_id = invoice["id"]

        invoice_total = float(
            invoice.get("total_amount") or 0
        )

        amount_paid = sum(
            float(payment.get("amount") or 0)
            for payment in existing_payments
            if payment["invoice_id"] == invoice_id
        )

        balance = invoice_total - amount_paid

        invoice_balances[invoice_id] = {
            "total": invoice_total,
            "paid": amount_paid,
            "balance": balance
        }

    # Only show invoices that still have money due
    unpaid_invoices = [
        invoice
        for invoice in payment_invoices
        if invoice_balances[invoice["id"]]["balance"] > 0
        and invoice.get("status") != "Cancelled"
    ]

    # -----------------------------
    # RECORD PAYMENT
    # -----------------------------

    with st.expander("➕ Record Payment"):

        if not unpaid_invoices:
            st.info("There are no invoices with an outstanding balance.")

        else:

            payment_invoice_id = st.selectbox(
                "Invoice",
                [invoice["id"] for invoice in unpaid_invoices],
                format_func=lambda invoice_id: next(
                    f'{invoice["invoice_number"]} - '
                    f'{payment_customer_names.get(invoice["customer_id"], "Unknown")}'
                    for invoice in unpaid_invoices
                    if invoice["id"] == invoice_id
                )
            )

            selected_payment_invoice = next(
                invoice
                for invoice in unpaid_invoices
                if invoice["id"] == payment_invoice_id
            )

            balance_info = invoice_balances[payment_invoice_id]

            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(
                    "Invoice Total",
                    f'{balance_info["total"]:.2f}'
                )

            with col2:
                st.metric(
                    "Already Paid",
                    f'{balance_info["paid"]:.2f}'
                )

            with col3:
                st.metric(
                    "Balance Due",
                    f'{balance_info["balance"]:.2f}'
                )

            with st.form("record_payment_form"):

                payment_date = st.date_input(
                    "Payment date",
                    value=date.today()
                )

                amount = st.number_input(
                    "Amount",
                    min_value=0.01,
                    max_value=float(balance_info["balance"]),
                    value=float(balance_info["balance"]),
                    step=0.01
                )

                payment_method = st.selectbox(
                    "Payment method",
                    [
                        "Cash",
                        "Bank Transfer",
                        "Cheque",
                        "Credit Card",
                        "Other"
                    ]
                )

                reference = st.text_input(
                    "Reference"
                )

                payment_notes = st.text_area(
                    "Notes"
                )

                payment_submitted = st.form_submit_button(
                    "Save Payment"
                )

                if payment_submitted:

                    supabase.table("payments").insert({
                        "invoice_id": payment_invoice_id,
                        "payment_date": str(payment_date),
                        "amount": amount,
                        "payment_method": payment_method,
                        "reference": reference,
                        "notes": payment_notes
                    }).execute()

                    new_paid_total = (
                        balance_info["paid"] + amount
                    )

                    new_balance = (
                        balance_info["total"] - new_paid_total
                    )

                    # Automatically update invoice status
                    if new_balance <= 0.01:
                        new_status = "Paid"
                    else:
                        new_status = "Unpaid"

                    (
                        supabase
                        .table("invoices")
                        .update({
                            "status": new_status
                        })
                        .eq("id", payment_invoice_id)
                        .execute()
                    )

                    st.success("Payment recorded successfully.")
                    st.rerun()

    # -----------------------------
    # PAYMENT HISTORY
    # -----------------------------

    st.subheader("Payment History")

    if existing_payments:

        display_payments = []

        for payment in existing_payments:

            related_invoice = next(
                (
                    invoice
                    for invoice in payment_invoices
                    if invoice["id"] == payment["invoice_id"]
                ),
                None
            )

            if related_invoice:

                display_payments.append({
                    "Payment Date": payment["payment_date"],
                    "Invoice": related_invoice["invoice_number"],
                    "Customer": payment_customer_names.get(
                        related_invoice["customer_id"],
                        "Unknown"
                    ),
                    "Amount": payment["amount"],
                    "Method": payment["payment_method"],
                    "Reference": payment["reference"]
                })

        st.dataframe(
            display_payments,
            use_container_width=True
        )

    else:
        st.info("No payments recorded yet.")
