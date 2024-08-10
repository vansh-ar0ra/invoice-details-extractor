import streamlit as st
import time
import os
import asyncio
from invoice_details_extractor import extract_details_from_invoice

def display_product_table(products):
    st.subheader("Products")
    for i, product in enumerate(products):
        cols = st.columns(4)
        with cols[0]:
            product['name'] = st.text_input(f"Product Name {i+1}", value=product.get('name', ''))
        with cols[1]:
            product['rate'] = st.number_input(f"Rate {i+1}", value=float(product.get('rate', 0.0)), min_value=0.0, format="%.2f")
        with cols[2]:
            product['quantity'] = st.number_input(f"Quantity {i+1}", value=float(product.get('quantity', 0.0)), min_value=0.0, format="%.2f")
        with cols[3]:
            product['total'] = st.number_input(f"Amount {i+1}", value=float(product.get('total', 0.0)), min_value=0.0, format="%.2f")

    # Add a new row button
    if st.button("Add New Product"):
        products.append({'name': '', 'rate': 0.0, 'quantity': 0.0})

    return products

# UI Layout
st.set_page_config(layout="wide")
st.title("Invoice Details Extractor")
st.markdown("##### Upload your Invoice on the File Uploader on the left. Click on Extract Details from Invoice button to fill the fields on the right using AI.")
st.markdown("###### Note: This application doesn't store any data. All the extracted data is stored in the session state. You can reset the application by clicking on the Reset button.")

reset_button_placeholder = st.empty()
with reset_button_placeholder.container():
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("Reset"):
            st.session_state.uploaded_file = None
            uploaded_file = None
            if os.path.exists("temp.pdf"):
                os.remove("temp.pdf")
            st.session_state.details = None  # Clear the extracted details


with st.sidebar:
    mistral_api_key = st.text_input("Mistral API Key", key="langchain_search_api_key_openai", type="password")


left_column, right_column = st.columns(2)

# Left half: File upload
with left_column:
    st.write("") 
    st.markdown("#### ← Please add the API key using the left sidebar before uploading the file.")
    uploaded_file = st.file_uploader("Upload a file", type=None)

    if uploaded_file is not None:
        st.session_state.details = None
    
    # Disable the Extract Details button if no file is uploaded
    extract_details_button = st.button("Extract Details from Invoice", 
                                       key="extract_details", 
                                       help="Click to extract details from the uploaded invoice",
                                       disabled=uploaded_file is None)

    
if 'details' not in st.session_state:
    st.session_state.details = None


# Right half: Form
with right_column:
    form_placeholder = st.empty()

    if uploaded_file and extract_details_button and st.session_state.details is None:
        if not mistral_api_key:
            st.info("Please add your Mistral API key to continue.")
            st.stop()

        with open("temp.pdf", "wb") as f:
            f.write(uploaded_file.getbuffer())

        # Display loading message in the right column while processing
        with form_placeholder.container():
            st.info("Processing the uploaded file...")

        start_time = time.time()
        details = asyncio.run(extract_details_from_invoice("temp.pdf", mistral_api_key))

        while time.time() - start_time < 10:
            if details:
                break
            time.sleep(1)  # Briefly wait before checking again

        if not details:
            st.error("The information could not be extracted by the LLM. Please check if the uploaded file is an invoice or add the information manually.")
            st.stop()

        st.session_state.details = details

    # Render the form with the extracted or existing details
    if st.session_state.details:
        with form_placeholder.container():
            st.subheader("Customer Details")
            customer_details = st.session_state.details.get('customer_details', {})
            name = st.text_input("Name", value=customer_details.get('name', ''))
            address = st.text_area("Address", value=customer_details.get('address', ''))
            phone = st.text_input("Phone Number", value=customer_details.get('phone', ''))
            email = st.text_input("Email ID", value=customer_details.get('email', ''))
            products = display_product_table(st.session_state.details.get('products', []))

            st.subheader("Total Amount")
            total_amount_details = st.session_state.details.get("total_amount", {})
            currency, total_amount = st.columns(2)
            with currency:
                currency_input = st.text_input("Currency", value=total_amount_details.get('currency', ''))
            with total_amount:
                total_amount_input = st.number_input("Total Amount", value=float(total_amount_details.get('amount', 0.0)), format="%.2f")

    else:
        with form_placeholder.container():
            st.subheader("Customer Details")
            name = st.text_input("Name")
            address = st.text_area("Address")
            phone = st.text_input("Phone Number")
            email = st.text_input("Email ID")

            display_product_table([])

            st.subheader("Total Amount")
            currency, total_amount = st.columns(2)
            with currency:
                st.text_input("Currency")
            with total_amount:
                st.number_input("Total Amount", format="%.2f")
