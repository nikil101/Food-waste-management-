# 🍱 Local Food Wastage Management System

A Full-Stack Data Application designed to bridge the gap between commercial food surplus providers (restaurants, caterers, grocery stores) and verified beneficiaries/NGOs. This platform combines a robust **MySQL relational database** with an interactive **Python Streamlit dashboard** to provide real-time tracking, analytical metrics, and effortless inventory management.


## 📌 Project Overview & Purpose

Commercial food hubs generate massive amounts of surplus food daily, which frequently goes to waste due to a lack of immediate connection channels with NGOs and local feeding shelters. 

The **Local Food Wastage Management System** solves this operational challenge by digitizing the donation lifecycle. It abstracts complex backend relational database commands into a streamlined, automated portal, allowing non-technical operators to track surplus items, monitor claim fulfillments, and visualize environmental metrics dynamically.

---

## 🛠️ Tech Stack Used

* **Backend Database & Storage Layer:** MySQL RDBMS
* **Frontend UI Framework:** Streamlit
* **Data Engineering & Abstraction Layer:** Python 3.x, Pandas, SQLAlchemy
* **Database Driver Dialect:** `mysql-connector-python` & `pymysql`
* **Data Visualization:** Plotly Express

---

## 📦 Database Schema Architecture

The data ecosystem is fully normalized across four primary transactional tables inside the `food_waste_management` database:
1.  **`providers`**: Tracks registration details, entity classifications (e.g., Restaurant vs. Grocery Store), contact records, and urban hub locations.
2.  **`receivers`**: Houses verified organizational profile logs for NGOs and local charities.
3.  **`food_listings`**: Monitors real-time surplus allocations, quantity units, food type (Vegetarian/Vegan), and expiration windows.
4.  **`claims`**: Serves as the central transactional ledger connecting providers to receivers with state management labels (`Pending`, `Completed`, `Cancelled`).

---

## 📊 Core Features & Walkthrough of Key Visuals

### 📈 High-Level KPI Matrix
Provides immediate operational assessment metrics directly from live SQL counts:
* **Total Food Providers Registered:** Dynamic scalar count of food hubs.
* **Total Registered Beneficiaries/NGOs:** Total active distribution network connections.
* **Total Food Items Available:** Running metric sum of available food units in circulation.

### 🔍 Specialized Analytical Visuals & Operations
* **Top Provider Types Contributing Food:** A live Plotly bar chart running a joined query between `providers` and `food_listings` to aggregate total volume weight across business sectors.
* **Food Claim Fulfillment Ratios:** An interactive Plotly pie chart mapping active logistical statuses to show operational efficiency.
* **Contextual Filtering System:** A search module utilizing parameterized queries (`:city`) to safely look up provider coordinates without risk of SQL injection vulnerabilities.
* **Interactive CRUD Tabs:** Full interface support allowing users to run `INSERT` entries, execute status updates, or trigger record maintenance purges directly from the web interface.

---

## 📸 Dashboard Preview

### 1. Project Overview & Platform Health
![Platform Health Snapshot](https://github.com/nikil101/Food-waste-management-/blob/main/1.png?raw=true)

### 2. Live Interactive SQL Analytics Dashboard
![SQL Analytics Dashboard](https://github.com/nikil101/Food-waste-management-/blob/main/2.png?raw=true)

### 3. Database Management Operations Panel (CRUD)
![CRUD Operations Management](https://github.com/nikil101/Food-waste-management-/blob/main/3.png?raw=true)

---

