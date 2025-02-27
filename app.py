# VERSI 2

import streamlit as st
from recommendations import recommend_user_based, recommend_item_based

# Banner Section
st.image("ecommerce_banner.jpg", use_column_width=True, caption="Olist's Personalized E-commerce Hub")
st.title("Olist E-commerce Recommendation System - Internal Demo")
st.markdown("""

Welcome, Olist Marketing Team!

This demo presents a **draft version** of our E-commerce Recommendation System developed by our Data Science team. The system leverages both **User-Based** and **Item-Based Collaborative Filtering** to generate personalized product suggestions.

**What This Demo Offers:**
- **User-Based Filtering:** Recommends products by analyzing similarities between customer behaviors.
- **Item-Based Filtering:** Suggests products that are similar to a given product, based on historical review data.
- **Real-Time Testing:** Input a Customer Unique ID or Product ID to see immediate recommendation outputs.
- **Feedback-Driven Development:** This prototype is intended for internal evaluation. Your insights on performance, usability, and output quality are critical as we refine the system.

Please explore the demo, test various scenarios, and provide your feedback so we can further enhance our recommendation engine.

Thank you for your collaboration and support in driving innovation at Olist!
""")

# Sidebar: Recommendation Settings
st.sidebar.header("Recommendation Settings")
rec_type = st.sidebar.radio("Select Recommendation Type:", ("User-Based", "Item-Based"))

# Function to display recommendations in a grid format
def display_recommendations_grid(recommendations):
    cols = st.columns(3)  # 3 columns per row
    for idx, rec in enumerate(recommendations):
        # For illustration, assuming each rec is a dict with 'name' and 'image_url'
        # If you only have text recommendations, simply use st.write()
        col = cols[idx % 3]
        with col:
            # Display product image; if not available, use a default placeholder
            image_url = rec.get("image_url", "placeholder1.jpg")
            st.image(image_url, width=150)
            st.write(rec["name"])

if rec_type == "User-Based":
    customer_id = st.sidebar.text_input("Enter Your Customer Unique ID:")
    rec_button = st.sidebar.button("Get User-Based Recommendations")
    if rec_button:
        if not customer_id:
            st.error("Please enter a valid Customer Unique ID.")
        else:
            with st.spinner("Generating recommendations..."):
                recommendations = recommend_user_based(customer_id)
            st.subheader("Recommended Products for You")
            # Check if recommendations is a list of strings; if so, wrap them in a dict for demo
            if isinstance(recommendations, list) and recommendations and isinstance(recommendations[0], str):
                # Convert to dict format with placeholder image if you don't have actual URLs
                recommendations = [{"name": rec, "image_url": "placeholder1.jpg"} for rec in recommendations]
            if isinstance(recommendations, list):
                display_recommendations_grid(recommendations)
            else:
                st.write(recommendations)
else:
    product_id = st.sidebar.text_input("Enter a Product ID:")
    rec_button = st.sidebar.button("Get Item-Based Recommendations")
    if rec_button:
        if not product_id:
            st.error("Please enter a valid Product ID.")
        else:
            with st.spinner("Generating recommendations..."):
                recommendations = recommend_item_based(product_id)
            st.subheader("Similar Products You Might Like")
            if isinstance(recommendations, list) and recommendations and isinstance(recommendations[0], str):
                recommendations = [{"name": rec, "image_url": "placeholder1.jpg"} for rec in recommendations]
            if isinstance(recommendations, list):
                display_recommendations_grid(recommendations)
            else:
                st.write(recommendations)

st.markdown("---")
st.markdown("*Built with Streamlit for internal Olist's e-commerce team.*")


