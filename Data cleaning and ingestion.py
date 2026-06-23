import pandas as pd
from sqlalchemy import create_engine
from urllib.parse import quote_plus

# ==========================================
# 1. DATABASE CONNECTION SETUP
# ==========================================

USER = "root"
PASSWORD = quote_plus("Nikhil@123")
HOST = "localhost"
PORT = "3306"
DATABASE = "food_waste_management"

# Create SQLAlchemy Engine
engine = create_engine(
    f"mysql+pymysql://{USER}:{PASSWORD}@{HOST}:{PORT}/{DATABASE}"
)

# ==========================================
# 2. LOAD DATASETS
# ==========================================

print("⏳ Loading datasets...")

df_providers = pd.read_csv("providers_data.csv", encoding="utf-8")
df_receivers = pd.read_csv("receivers_data.csv", encoding="utf-8")
df_listings = pd.read_csv("food_listings_data.csv", encoding="utf-8")
df_claims = pd.read_csv("claims_data.csv", encoding="utf-8")

# ==========================================
# 3. CLEAN DATA
# ==========================================

print("🧹 Cleaning data...")

# Food Listings Date Cleaning
df_listings["Expiry_Date"] = pd.to_datetime(
    df_listings["Expiry_Date"],
    format="mixed",
    errors="coerce"
).dt.strftime("%Y-%m-%d")

# Claims Timestamp Cleaning
df_claims["Timestamp"] = pd.to_datetime(
    df_claims["Timestamp"],
    format="mixed",
    errors="coerce"
).dt.strftime("%Y-%m-%d %H:%M:%S")

# Check for invalid dates
print("Invalid Expiry Dates:", df_listings["Expiry_Date"].isna().sum())
print("Invalid Timestamps:", df_claims["Timestamp"].isna().sum())

# ==========================================
# 4. LOAD DATA INTO MYSQL
# ==========================================

print("🚀 Uploading tables to MySQL...")

df_providers.to_sql(
    name="providers",
    con=engine,
    if_exists="replace",
    index=False
)

df_receivers.to_sql(
    name="receivers",
    con=engine,
    if_exists="replace",
    index=False
)

df_listings.to_sql(
    name="food_listings",
    con=engine,
    if_exists="replace",
    index=False
)

df_claims.to_sql(
    name="claims",
    con=engine,
    if_exists="replace",
    index=False
)

# ==========================================
# 5. VERIFY TABLES
# ==========================================

print("\n✅ Data loaded successfully!")

print("\nProviders Preview:")
print(pd.read_sql("SELECT * FROM providers LIMIT 5", engine))

print("\nReceivers Preview:")
print(pd.read_sql("SELECT * FROM receivers LIMIT 5", engine))

print("\nFood Listings Preview:")
print(pd.read_sql("SELECT * FROM food_listings LIMIT 5", engine))

print("\nClaims Preview:")
print(pd.read_sql("SELECT * FROM claims LIMIT 5", engine))

print("\n🎉 All tables successfully loaded into MySQL!")