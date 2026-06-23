import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text
import plotly.express as px

import urllib.parse  # Built-in Python library to handle special characters

# ==========================================
# 1. DATABASE CONNECTION CONFIGURATION
# ==========================================
USER = "root"
RAW_PASSWORD = "Nikhil@123"
HOST = "localhost"
PORT = "3306"
DATABASE = "food_waste_management"

# This cleanly converts the '@' in your password to '%40' so SQLAlchemy doesn't break
PASSWORD = urllib.parse.quote_plus(RAW_PASSWORD)

@st.cache_resource
def get_db_engine():
    # Using mysql+mysqlconnector bypasses the security plugin errors automatically
    base_url = f"mysql+mysqlconnector://{USER}:{PASSWORD}@{HOST}:{PORT}"
    base_engine = create_engine(base_url)
    
    # Ensure the database workspace container is active
    with base_engine.connect() as conn:
        conn.execute(text(f"CREATE DATABASE IF NOT EXISTS {DATABASE}"))
        
    return create_engine(f"{base_url}/{DATABASE}")

try:
    engine = get_db_engine()
except Exception as e:
    st.error(f"Database Connection Error: {e}")

# ==========================================
# 2. APP CONFIGURATION & NAVIGATION
# ==========================================
st.set_page_config(page_title="Local Food Wastage Management System", layout="wide")

st.sidebar.title("🍱 Navigation Menu")
page = st.sidebar.radio("Go to:", ["Project Overview", "SQL Analytics Dashboard", "Manage Listings & Claims (CRUD)"])

# ==========================================
# PAGE 1: PROJECT OVERVIEW
# ==========================================
if page == "Project Overview":
    st.title("📌 Local Food Wastage Management System")
    st.markdown("""
    ### Problem Statement
    Food wastage is a significant global issue, with households and restaurants discarding surplus food while thousands face food insecurity[cite: 3]. This system bridges the gap between surplus providers and those in need through a structured data platform[cite: 10, 11].
    
    ### Tech Stack Used:
    * **Backend:** MySQL Database [cite: 19]
    * **Frontend:** Streamlit Web Framework [cite: 25]
    * **Data Processing & Analytics:** Python, Pandas, SQLAlchemy [cite: 15, 112]
    """)
    
    # Simple Metrics Cards
    st.subheader("📊 Platform Health Snapshot")
    col1, col2, col3 = st.columns(3)
    
    try:
        with engine.connect() as conn:
            total_providers = conn.execute(text("SELECT COUNT(*) FROM providers")).scalar()
            total_receivers = conn.execute(text("SELECT COUNT(*) FROM receivers")).scalar()
            total_food = conn.execute(text("SELECT SUM(Quantity) FROM food_listings")).scalar() or 0
            
        col1.metric("Total Food Providers Registered", total_providers)
        col2.metric("Total Registered Beneficiaries/NGOs", total_receivers)
        col3.metric("Total Food Items Available (Units)", total_food)
    except Exception as db_err:
        st.warning("⚠️ Database tables appear empty. Please verify that your ingestion pipeline script has been completely executed.")

# ==========================================
# PAGE 2: SQL ANALYTICS DASHBOARD
# ==========================================
elif page == "SQL Analytics Dashboard":
    st.title("📊 Data Insights & Trend Analysis")
    st.caption("Real-time metrics parsed straight from the SQL database layer.")
    
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("💡 Top Provider Types Contributing Food")
        q2_query = """
        SELECT p.Type AS Provider_Type, SUM(f.Quantity) AS Total_Food_Donated
        FROM providers p
        JOIN food_listings f ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Type
        ORDER BY Total_Food_Donated DESC;
        """
        try:
            df_q2 = pd.read_sql(q2_query, engine)
            if not df_q2.empty:
                fig_q2 = px.bar(df_q2, x="Provider_Type", y="Total_Food_Donated", color="Provider_Type", labels={"Total_Food_Donated":"Units Donated"})
                st.plotly_chart(fig_q2, use_container_width=True)
            else:
                st.info("No provider listings data currently available.")
        except Exception as e:
            st.error(f"Could not load data: {e}")

    with col_right:
        st.subheader("📈 Food Claim Fulfillment Ratios")
        q10_query = """
        SELECT Status, COUNT(*) AS Claim_Count
        FROM claims
        GROUP BY Status;
        """
        try:
            df_q10 = pd.read_sql(q10_query, engine)
            if not df_q10.empty:
                fig_q10 = px.pie(df_q10, values="Claim_Count", names="Status", hole=0.4, color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig_q10, use_container_width=True)
            else:
                st.info("No claims records currently available.")
        except Exception as e:
            st.error(f"Could not load data: {e}")

    st.subheader("🔍 Look Up Providers by Location")
    try:
        city_list = ["All"] + pd.read_sql("SELECT DISTINCT City FROM providers", engine)["City"].tolist()
        selected_city = st.selectbox("Select Target City Filter:", city_list)
        
        if selected_city == "All":
            search_query = "SELECT Name, Type, Contact, Address, City FROM providers"
            df_search = pd.read_sql(search_query, engine)
        else:
            search_query = text("SELECT Name, Type, Contact, Address, City FROM providers WHERE City = :city")
            df_search = pd.read_sql(search_query, engine, params={"city": selected_city})
            
        st.dataframe(df_search, use_container_width=True)
    except Exception as e:
        st.error(f"Table retrieval failed: {e}")

# ==========================================
# PAGE 3: MANAGE LISTINGS & CLAIMS (CRUD Operations)
# ==========================================
elif page == "Manage Listings & Claims (CRUD)":
    st.title("⚙️ Database Operations Panel (CRUD)")
    
    tab1, tab2, tab3 = st.tabs(["➕ Create Food Listing", "🔄 Update Claim Status", "🗑️ Delete Record"])
    
    with tab1:
        st.subheader("Submit Surplus Food Supply")
        with st.form("insert_form", clear_on_submit=True):
            f_name = st.text_input("Food Item Name (e.g., Rice, Apples)")
            qty = st.number_input("Quantity Available (Units)", min_value=1, value=10)
            exp_date = st.date_input("Expiry Window Date")
            p_id = st.number_input("Your Provider ID Number", min_value=1, value=1)
            f_type = st.selectbox("Food Categorization Type", ["Vegetarian", "Non-Vegetarian", "Vegan"])
            m_type = st.selectbox("Meal Category Classification", ["Breakfast", "Lunch", "Dinner", "Snacks"])
            loc = st.text_input("City Location Name")
            
            submit = st.form_submit_button("Commit Entry to SQL Table")
            
        if submit:
            insert_sql = text("""
                INSERT INTO food_listings (Food_Name, Quantity, Expiry_Date, Provider_ID, Food_Type, Meal_Type, Location)
                VALUES (:name, :qty, :exp, :pid, :ftype, :mtype, :loc)
            """)
            try:
                with engine.begin() as conn:
                    conn.execute(insert_sql, {"name": f_name, "qty": qty, "exp": exp_date, "pid": p_id, "ftype": f_type, "mtype": m_type, "loc": loc})
                st.success(f"🎉 '{f_name}' has been safely injected into the SQL database.")
            except Exception as e:
                st.error(f"Insertion failed: {e}")

    with tab2:
        st.subheader("Modify Active Claim Status Code")
        claim_id = st.number_input("Target Claim ID Number:", min_value=1, step=1)
        new_status = st.selectbox("Assign Status Label:", ["Pending", "Completed", "Cancelled"])
        
        if st.button("Apply Status Modification Update"):
            update_sql = text("UPDATE claims SET Status = :status WHERE Claim_ID = :id")
            try:
                with engine.begin() as conn:
                    conn.execute(update_sql, {"status": new_status, "id": claim_id})
                st.success(f"✅ Status updated to '{new_status}' for Claim ID {claim_id}.")
            except Exception as e:
                st.error(f"Update failed: {e}")

    with tab3:
        st.subheader("Remove Inventory (Data Maintenance)")
        food_id = st.number_input("Target Food Listing ID to Delete:", min_value=1, step=1)
        
        if st.button("Permanently Purge Record", type="primary"):
            delete_sql = text("DELETE FROM food_listings WHERE Food_ID = :id")
            try:
                with engine.begin() as conn:
                    conn.execute(delete_sql, {"id": food_id})
                st.warning(f"🗑️ Food Item Record ID {food_id} has been completely dropped from your local system schema.")
            except Exception as e:
                st.error(f"Deletion failed: {e}")