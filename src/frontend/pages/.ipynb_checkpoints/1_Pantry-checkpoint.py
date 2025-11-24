import streamlit as st
from utils.api import add_pantry, get_pantry, delete_pantry_item

st.title("🥫 Pantry Manager")

token = st.session_state.get("token")

if not token:
    st.error("Please login first.")
    st.stop()

# Add item section
st.subheader("Add Pantry Item")
name = st.text_input("Name")
category = st.text_input("Category")
expiry = st.date_input("Expiry Date")
quantity = st.number_input("Quantity", min_value=1, step=1)

if st.button("Add Item"):
    payload = {
        "name": name,
        "category": category,
        "expiry_date": str(expiry),
        "quantity": int(quantity)
    }
    r = add_pantry(token, payload)
    if r["code"] == 201:
        st.success("Item added!")
    else:
        st.error(r["message"])

# List items
st.subheader("Your Pantry Items")
resp = get_pantry(token)

if resp["code"] == 200 and resp["data"]:
    for item in resp["data"]:
        with st.container():
            st.write(f"### {item['name']}")
            st.write(f"Category: {item.get('category', '-')}")
            st.write(f"Expiry: {item.get('expiry_date', '-')}")
            st.write(f"Quantity: {item.get('quantity', '-')}")
            
            if st.button(f"Delete {item['id']}"):
                delete_pantry_item(token, item["id"])
                st.rerun()
else:
    st.info("No items yet.")