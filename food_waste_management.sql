#create database food_waste_management;
use food_waste_management;

-- =====================================================================
-- LOCAL FOOD WASTAGE MANAGEMENT SYSTEM - ANALYTICS INVENTORY SCRIPT
-- =====================================================================
-- Target Database Environment: MySQL
-- Pre-requisite: Run the Python ingestion script to generate and populate tables.

USE your_database_name;

-- ---------------------------------------------------------------------
-- CATEGORY 1: FOOD PROVIDERS & RECEIVERS
-- ---------------------------------------------------------------------

-- Q1: How many food providers and receivers are there in each city?
-- Purpose: Analyzes geographic distribution of platform stakeholders[cite: 80].
SELECT 
    COALESCE(p.City, r.City) AS City,
    COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
    COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM providers p
LEFT JOIN receivers r ON p.City = r.City
GROUP BY COALESCE(p.City, r.City)
UNION
SELECT 
    COALESCE(p.City, r.City) AS City,
    COUNT(DISTINCT p.Provider_ID) AS Total_Providers,
    COUNT(DISTINCT r.Receiver_ID) AS Total_Receivers
FROM providers p
RIGHT JOIN receivers r ON p.City = r.City
GROUP BY COALESCE(p.City, r.City);


-- Q2: Which type of food provider (restaurant, grocery store, etc.) contributes the most food?
-- Purpose: Identifies high-impact donation pipelines to scale partnerships[cite: 81].
SELECT 
    p.Type AS Provider_Type,
    SUM(f.Quantity) AS Total_Food_Donated
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Type
ORDER BY Total_Food_Donated DESC;


-- Q3: What is the contact information of food providers in a specific city?
-- Purpose: Operational query utilized inside the Streamlit UI to coordinate pick-ups[cite: 28, 82].
SELECT Name, Type, Contact, Address, City
FROM providers
WHERE City = 'Mumbai'  -- Dynamic filter variable placeholder for UI
ORDER BY Name;


-- Q4: Which receivers have claimed the most food?
-- Purpose: Tracks allocation distribution to monitor NGO capacity[cite: 83].
SELECT 
    r.Name AS Receiver_Name, 
    r.Type AS Receiver_Type, 
    COUNT(c.Claim_ID) AS Total_Claims_Made
FROM receivers r
JOIN claims c ON r.Receiver_ID = c.Receiver_ID
GROUP BY r.Receiver_ID, r.Name, r.Type
ORDER BY Total_Claims_Made DESC;


-- ---------------------------------------------------------------------
-- CATEGORY 2: FOOD LISTINGS & AVAILABILITY
-- ---------------------------------------------------------------------

-- Q5: What is the total quantity of food available from all providers?
-- Purpose: Baseline tracking metric for system supply[cite: 85].
SELECT SUM(Quantity) AS Total_Global_Available_Food 
FROM food_listings;


-- Q6: Which city has the highest number of food listings?
-- Purpose: Exposes where surplus operations are most heavily focused[cite: 86].
SELECT Location AS City, COUNT(Food_ID) AS Total_Food_Listings
FROM food_listings
GROUP BY Location
ORDER BY Total_Food_Listings DESC
LIMIT 1;


-- Q7: What are the most commonly available food types?
-- Purpose: Understands supply characteristics (e.g., Vegetarian, Vegan, Non-Veg)[cite: 68, 87].
SELECT Food_Type, COUNT(*) AS Total_Listings, SUM(Quantity) AS Total_Quantity
FROM food_listings
GROUP BY Food_Type
ORDER BY Total_Quantity DESC;


-- ---------------------------------------------------------------------
-- CATEGORY 3: CLAIMS & DISTRIBUTION
-- ---------------------------------------------------------------------

-- Q8: How many food claims have been made for each food item?
-- Purpose: Analyzes listing item popularities and structural clearance rates[cite: 89].
SELECT f.Food_Name, COUNT(c.Claim_ID) AS Total_Claims
FROM food_listings f
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Food_ID, f.Food_Name
ORDER BY Total_Claims DESC;


-- Q9: Which provider has had the highest number of successful food claims?
-- Purpose: Measures real-world platform utility by matching listings to execution[cite: 90].
SELECT p.Name AS Provider_Name, COUNT(c.Claim_ID) AS Successful_Claims
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
JOIN claims c ON f.Food_ID = c.Food_ID
WHERE c.Status = 'Completed'
GROUP BY p.Provider_ID, p.Name
ORDER BY Successful_Claims DESC
LIMIT 1;



-- Q10: What percentage of food claims are completed vs. pending vs. canceled?
-- Purpose: Key administrative performance metric evaluating system logistical efficiency[cite: 91, 110].
SELECT 
    Status,
    COUNT(*) AS Claim_Count,
    ROUND((COUNT(*) * 100.0 / (SELECT COUNT(*) FROM claims)), 2) AS Percentage
FROM claims
GROUP BY Status;


-- ---------------------------------------------------------------------
-- CATEGORY 4: DEEP-DIVE ANALYSIS & INSIGHTS
-- ---------------------------------------------------------------------

-- Q11: What is the average quantity of food claimed per receiver?
-- Purpose: Aids in identifying order sizes and structural storage demands[cite: 93].
SELECT r.Name, AVG(f.Quantity) AS Avg_Quantity_Claimed
FROM receivers r
JOIN claims c ON r.Receiver_ID = c.Receiver_ID
JOIN food_listings f ON c.Food_ID = f.Food_ID
WHERE c.Status = 'Completed'
GROUP BY r.Receiver_ID, r.Name;


-- Q12: Which meal type (breakfast, lunch, dinner, snacks) is claimed the most?
-- Purpose: Identifies operational urgency spikes across timeline components[cite: 94].
SELECT f.Meal_Type, COUNT(c.Claim_ID) AS Total_Claims
FROM food_listings f
JOIN claims c ON f.Food_ID = c.Food_ID
GROUP BY f.Meal_Type
ORDER BY Total_Claims DESC;


-- Q13: What is the total quantity of food donated by each provider?
-- Purpose: Tracks raw historical volume metrics per single merchant entity[cite: 95].
SELECT p.Name, p.Type, SUM(f.Quantity) AS Total_Quantity_Donated
FROM providers p
JOIN food_listings f ON p.Provider_ID = f.Provider_ID
GROUP BY p.Provider_ID, p.Name, p.Type
ORDER BY Total_Quantity_Donated DESC;


-- Q14: Are there any food items listed that have expired before being claimed?
-- Purpose: Crucial metric for measuring food wastage within the management system platform itself[cite: 105].
SELECT f.Food_Name, f.Expiry_Date, f.Quantity, p.Name AS Provider_Name
FROM food_listings f
JOIN providers p ON f.Provider_ID = p.Provider_ID
LEFT JOIN claims c ON f.Food_ID = c.Food_ID
WHERE f.Expiry_Date < CURDATE() 
  AND (c.Status IS NULL OR c.Status != 'Completed');


-- Q15: What is the monthly trend of food claims being made?
-- Purpose: Highlights operational trajectory and timeline spikes for planning milestones.
SELECT 
    LEFT(`Timestamp`, 7) AS Month_Period,
    COUNT(Claim_ID) AS Total_Claims
FROM claims
GROUP BY LEFT(`Timestamp`, 7)
ORDER BY Month_Period;
