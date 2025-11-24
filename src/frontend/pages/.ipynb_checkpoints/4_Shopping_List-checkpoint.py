# frontend/pages/4_Shopping_List.py

import streamlit as st
from typing import Any, Dict, List, Optional

from utils.api import get_pantry, create_shopping_list

st.set_page_config(page_title="Shopping List", page_icon="🛒", layout="wide")

# -------- Authentication check --------
token = st.session_state.get("token")
if not token:
    st.warning("Please log in first.")
    st.stop()

st.title("🛒 Generate Shopping List")

# -------- Load pantry --------
resp = get_pantry(token)
if resp["code"] >= 400:
    st.error(f"Failed to load pantry: {resp['message']}")
    st.stop()

pantry_items: List[Dict[str, Any]] = resp["data"] or []

st.subheader("Your Pantry Items")

if not pantry_items:
    st.info("Your pantry is empty. Add some items in the Pantry page.")
else:
    st.write("Items currently in pantry:")
    for item in pantry_items:
        st.markdown(f"- **{item['name']}** ({item['quantity']} {item.get('unit', '')})")

st.markdown("---")

# -------- Create shopping list --------

st.subheader("Create Shopping List From Recipe")

recipe_name = st.text_input("Recipe Name")
ingredients_text = st.text_area(
    "Recipe Ingredients (comma-separated)",
    placeholder="tomato, onion, chicken breast",
)

if st.button("Generate Shopping List"):
    if not recipe_name.strip():
        st.error("Please enter a recipe name.")
    elif not ingredients_text.strip():
        st.error("Please enter at least one ingredient.")
    else:
        ingredients = [x.strip() for x in ingredients_text.split(",") if x.strip()]

        resp = create_shopping_list(token, recipe_name, ingredients)

        if resp["code"] >= 400:
            st.error(f"Failed to create shopping list: {resp['message']}")
        else:
            st.success("Shopping list created successfully!")

            data = resp["data"]
            st.write(f"### Missing Ingredients for **{data['recipe_name']}**")
            for item in data["items"]:
                st.markdown(f"- **{item}**")

            st.info("Shopping list saved!")