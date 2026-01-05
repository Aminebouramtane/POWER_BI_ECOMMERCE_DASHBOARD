/*******************************************************************************
 * ENHANCED E-COMMERCE DATA WAREHOUSE SCHEMA
 * Optimized for Power BI Analytics
 * Date: January 5, 2026
 * Architecture: Star Schema with Snowflake Elements
 ******************************************************************************/

-- ===========================================================================
-- MODULE 1: CUSTOMER ANALYTICS
-- ===========================================================================

-- -------------------------
-- Dim_Client (Customer Dimension)
-- -------------------------
TABLE: Dim_Client
Primary Key: id_client
Columns:
  - id_client (INT) [PK]
  - prenom (VARCHAR)
  - nom (VARCHAR)
  - email (VARCHAR)
  - age (INT)
  - sexe (CHAR)
  - province (VARCHAR)
  - adresse (VARCHAR)
  - code_postal (VARCHAR)
  - ville (VARCHAR)
  - pays (VARCHAR)
  - canal_acquisition (VARCHAR)
  - date_inscription (DATETIME)
  - latitude (DECIMAL)
  - longitude (DECIMAL)

Foreign Keys:
  - id_region → Dim_Region.id_region (Geography Snowflake)

Indexes:
  - idx_client_region ON (ville, province, pays)
  - idx_client_acquisition ON (canal_acquisition)
  - idx_client_inscription ON (date_inscription)

Business Rules:
  - Email must be unique
  - Age range: 12-120
  - Gender: M/F/Other
  
-- -------------------------
-- Dim_Region (Geography Dimension) - SNOWFLAKE
-- -------------------------
TABLE: Dim_Region
Primary Key: id_region
Columns:
  - id_region (INT) [PK]
  - ville (VARCHAR)
  - region (VARCHAR)
  - pays (VARCHAR)
  - latitude (DECIMAL)
  - longitude (DECIMAL)
  - region_code (VARCHAR)
  - timezone (VARCHAR)

Hierarchy:
  Pays → Region → Ville

Indexes:
  - idx_region_pays ON (pays)
  - idx_region_composite ON (ville, region, pays)

-- -------------------------
-- Dim_Customer_Segment (NEW - Customer Segmentation)
-- -------------------------
TABLE: Dim_Customer_Segment
Primary Key: id_segment
Columns:
  - id_segment (INT) [PK]
  - segment_name (VARCHAR) -- VIP, Regular, Occasional, At Risk, Churned
  - segment_description (TEXT)
  - rfm_score (VARCHAR) -- e.g., "555" (Recency-Frequency-Monetary)
  - recency_score (INT) -- 1-5
  - frequency_score (INT) -- 1-5
  - monetary_score (INT) -- 1-5
  - min_clv (DECIMAL) -- Minimum Customer Lifetime Value
  - max_clv (DECIMAL) -- Maximum Customer Lifetime Value
  - is_active (BOOLEAN)

Business Segments:
  - Champions (555, 554, 544, 545)
  - Loyal Customers (543, 444, 435, 355)
  - Potential Loyalists (553, 551, 552, 541)
  - At Risk (255, 254, 245, 244)
  - Churned (111, 112, 121, 122)


-- ===========================================================================
-- MODULE 2: PRODUCT & INVENTORY
-- ===========================================================================

-- -------------------------
-- Dim_Produit (Product Dimension)
-- -------------------------
TABLE: Dim_Produit
Primary Key: id_produit
Columns:
  - id_produit (INT) [PK]
  - designation (VARCHAR)
  - categorie (VARCHAR)
  - marque (VARCHAR)
  - prix_achat (DECIMAL)
  - prix_vente (DECIMAL)
  - reference_produit (VARCHAR) -- SKU
  - id_centre_dist (INT) [FK]
  - department (VARCHAR)
  - marge_unitaire (DECIMAL) -- CALCULATED: prix_vente - prix_achat
  - taux_marge (DECIMAL) -- CALCULATED: (marge_unitaire / prix_vente) * 100
  - is_active (BOOLEAN)

Foreign Keys:
  - id_centre_dist → Distribution_Centers.id
  - id_category → Dim_Product_Category.id_category (Optional Snowflake)

Indexes:
  - idx_produit_categorie ON (categorie)
  - idx_produit_marque ON (marque)
  - idx_produit_sku ON (reference_produit)

Calculated Columns (Power BI):
  - Profit_Margin = prix_vente - prix_achat
  - Margin_Percentage = DIVIDE([Profit_Margin], prix_vente, 0) * 100

-- -------------------------
-- Dim_Product_Category (NEW - Product Hierarchy) - SNOWFLAKE
-- -------------------------
TABLE: Dim_Product_Category
Primary Key: id_category
Columns:
  - id_category (INT) [PK]
  - category_name (VARCHAR)
  - parent_category_id (INT) [FK] -- Self-referencing
  - category_level (INT) -- 1=Department, 2=Category, 3=Subcategory
  - department_name (VARCHAR)
  - category_description (TEXT)
  - display_order (INT)

Hierarchy:
  Department → Category → Subcategory

Examples:
  - Department: Women → Category: Accessories → Subcategory: Caps
  - Department: Men → Category: Active → Subcategory: Compression Wear

-- -------------------------
-- Distribution_Centers (Reference Data)
-- -------------------------
TABLE: Distribution_Centers
Primary Key: id
Columns:
  - id (INT) [PK]
  - name (VARCHAR)
  - latitude (DECIMAL)
  - longitude (DECIMAL)
  - city (VARCHAR)
  - state (VARCHAR)
  - capacity (INT)
  - is_operational (BOOLEAN)


-- ===========================================================================
-- MODULE 3: SALES & REVENUE (STAR SCHEMA - CORE)
-- ===========================================================================

-- -------------------------
-- Dim_Temps (Time Dimension) - ENHANCED
-- -------------------------
TABLE: Dim_Temps
Primary Key: id_temps
Columns:
  -- Primary Date Attributes
  - id_temps (INT) [PK]
  - date_complete (DATE) [UNIQUE]
  - jour (INT) -- 1-31
  - mois (INT) -- 1-12
  - annee (INT) -- YYYY
  
  -- Enhanced Calendar Attributes
  - nom_jour (VARCHAR) -- Monday, Tuesday, etc.
  - nom_mois (VARCHAR) -- January, February, etc.
  - jour_semaine (INT) -- 1=Monday, 7=Sunday
  - semaine_annee (INT) -- Week number (1-53)
  - jour_annee (INT) -- Day of year (1-366)
  
  -- Business Calendar
  - trimestre (INT) -- Q1, Q2, Q3, Q4
  - semestre (INT) -- H1, H2
  - trimestre_label (VARCHAR) -- "Q1 2024"
  - semestre_label (VARCHAR) -- "H1 2024"
  
  -- Fiscal Calendar (if different from calendar year)
  - fiscal_year (INT)
  - fiscal_quarter (INT)
  - fiscal_month (INT)
  
  -- Flags
  - is_weekend (BOOLEAN)
  - is_holiday (BOOLEAN)
  - is_working_day (BOOLEAN)
  - holiday_name (VARCHAR)
  
  -- Relative Time
  - is_current_day (BOOLEAN)
  - is_current_week (BOOLEAN)
  - is_current_month (BOOLEAN)
  - is_current_quarter (BOOLEAN)
  - is_current_year (BOOLEAN)

Indexes:
  - idx_temps_date ON (date_complete)
  - idx_temps_year_month ON (annee, mois)
  - idx_temps_quarter ON (annee, trimestre)

Power BI Time Intelligence:
  - Mark as Date Table
  - Set date_complete as the key column
  - Enable automatic date/time hierarchies

-- -------------------------
-- Dim_Canal (Channel Dimension)
-- -------------------------
TABLE: Dim_Canal
Primary Key: id_canal
Columns:
  - id_canal (INT) [PK]
  - nom_canal (VARCHAR)
  - type_canal (VARCHAR) -- Digital, Social Media, Marketplace, Retail
  - categorie_canal (VARCHAR) -- Acquisition, Retention, Direct, Vente
  - plateforme (VARCHAR)
  - marketplace_nom (VARCHAR)
  - ville_magasin (VARCHAR)
  - chiffre_affaires (DECIMAL) -- Aggregated metric
  - nombre_transactions (INT) -- Aggregated metric
  - cout_acquisition (DECIMAL) -- CAC per channel
  - is_active (BOOLEAN)

Hierarchy:
  Type_Canal → Categorie_Canal → Nom_Canal

Indexes:
  - idx_canal_type ON (type_canal)
  - idx_canal_categorie ON (categorie_canal)

-- -------------------------
-- FACT_Vente (Sales Fact Table) - ENHANCED
-- -------------------------
TABLE: Fact_Vente
Primary Key: id_vente
Grain: One row per order line item
Columns:
  -- Keys
  - id_vente (BIGINT) [PK]
  - id_temps (INT) [FK] → Dim_Temps
  - id_region (INT) [FK] → Dim_Region
  - id_client (INT) [FK] → Dim_Client
  - id_produit (INT) [FK] → Dim_Produit
  - id_canal (INT) [FK] → Dim_Canal
  - id_segment (INT) [FK] → Dim_Customer_Segment (Optional)
  
  -- Measures (Additive)
  - chiffre_affaire (DECIMAL) -- Revenue
  - quantite_vendue (INT)
  - panier_moyen (DECIMAL)
  - nombre_ventes (INT)
  
  -- NEW: Enhanced Measures
  - prix_achat_total (DECIMAL) -- Cost of goods sold
  - marge_brute (DECIMAL) -- CALCULATED: chiffre_affaire - prix_achat_total
  - taux_marge (DECIMAL) -- CALCULATED: (marge_brute / chiffre_affaire) * 100
  - remise_montant (DECIMAL) -- Discount amount
  - taux_remise (DECIMAL) -- Discount percentage
  - cout_livraison (DECIMAL) -- Shipping cost
  
  -- Degenerate Dimensions
  - order_id (VARCHAR)
  - order_status (VARCHAR) -- Complete, Cancelled, Returned, Processing
  - payment_method (VARCHAR) -- Credit Card, PayPal, etc.
  
  -- Timestamps
  - date_vente (DATETIME)
  - date_paiement (DATETIME)

Indexes:
  - idx_vente_temps ON (id_temps)
  - idx_vente_client ON (id_client)
  - idx_vente_produit ON (id_produit)
  - idx_vente_canal ON (id_canal)
  - idx_vente_date ON (date_vente)

Partitioning:
  - Partition by id_temps (monthly or quarterly)

Power BI Measures (DAX):
  - Total_Revenue = SUM(Fact_Vente[chiffre_affaire])
  - Total_Profit = SUM(Fact_Vente[marge_brute])
  - Profit_Margin_% = DIVIDE([Total_Profit], [Total_Revenue], 0)
  - Average_Order_Value = DIVIDE([Total_Revenue], DISTINCTCOUNT(Fact_Vente[order_id]))
  - Units_Sold = SUM(Fact_Vente[quantite_vendue])

-- -------------------------
-- Fact_Daily_Sales (NEW - Aggregate Fact for Performance)
-- -------------------------
TABLE: Fact_Daily_Sales
Primary Key: (id_temps, id_region, id_canal)
Grain: Daily aggregates by region and channel
Columns:
  - id_temps (INT) [FK] → Dim_Temps
  - id_region (INT) [FK] → Dim_Region
  - id_canal (INT) [FK] → Dim_Canal
  
  -- Aggregated Measures
  - total_revenue (DECIMAL)
  - total_orders (INT)
  - total_items (INT)
  - total_customers (INT)
  - avg_order_value (DECIMAL)
  - total_profit (DECIMAL)
  - avg_profit_margin (DECIMAL)

Purpose:
  - Pre-calculated for fast dashboard loading
  - Use for high-level KPI tiles
  - Reduce query time on large datasets


-- ===========================================================================
-- MODULE 4: LOGISTICS & FULFILLMENT
-- ===========================================================================

-- -------------------------
-- Dim_Livraison (Delivery Dimension)
-- -------------------------
TABLE: Dim_Livraison
Primary Key: id_livraison
Columns:
  - id_livraison (INT) [PK]
  - mode_livraison (VARCHAR) -- Standard, Express, Economy, Same Day, Next Day
  - type_livraison (VARCHAR) -- Domicile, Point Relais, Magasin, Bureau
  - delai_promis_jours (INT) -- Promised delivery days
  - cout_base (DECIMAL) -- Base shipping cost
  - sla_heures (INT) -- Service Level Agreement in hours
  - is_premium (BOOLEAN)
  - display_order (INT)

Business Rules:
  - Express: 1-2 days
  - Standard: 3-5 days
  - Economy: 5-7 days
  - Same Day: 0 days
  - Next Day: 1 day

-- -------------------------
-- Dim_Order_Status (NEW - Order Status Dimension)
-- -------------------------
TABLE: Dim_Order_Status
Primary Key: id_status
Columns:
  - id_status (INT) [PK]
  - status_name (VARCHAR) -- Complete, Shipped, Processing, Cancelled, Returned
  - status_category (VARCHAR) -- Success, In Progress, Failed
  - is_successful (BOOLEAN)
  - is_cancelled (BOOLEAN)
  - is_returned (BOOLEAN)
  - display_color (VARCHAR) -- For visualization
  - display_order (INT)

-- -------------------------
-- FACT_Livraison (Delivery Fact Table) - ENHANCED
-- -------------------------
TABLE: Fact_Livraison
Primary Key: id_fact_livraison
Grain: One row per order delivery
Columns:
  -- Keys
  - id_fact_livraison (BIGINT) [PK]
  - id_temps (INT) [FK] → Dim_Temps (order date)
  - id_livraison (INT) [FK] → Dim_Livraison
  - id_region (INT) [FK] → Dim_Region
  - id_client (INT) [FK] → Dim_Client
  - id_status (INT) [FK] → Dim_Order_Status
  
  -- NEW: Calculated Metrics
  - delai_traitement_heures (DECIMAL) -- Time from order to ship
  - delai_livraison_heures (DECIMAL) -- Time from ship to delivery
  - delai_total_heures (DECIMAL) -- Total delivery time
  - delai_vs_promis (DECIMAL) -- Actual - Promised (negative = early)
  - is_livraison_ontime (BOOLEAN) -- Met SLA?
  - is_livraison_retard (BOOLEAN) -- Late delivery?
  - cout_livraison (DECIMAL)
  - nombre_tentatives (INT) -- Delivery attempts
  
  -- Degenerate Dimensions
  - order_id (VARCHAR)
  - tracking_number (VARCHAR)
  
  -- Timestamps
  - date_commande (DATETIME)
  - date_expedition (DATETIME)
  - date_livraison (DATETIME)
  - date_retour (DATETIME)

Indexes:
  - idx_livraison_temps ON (id_temps)
  - idx_livraison_status ON (id_status)
  - idx_livraison_order ON (order_id)

Power BI Measures (DAX):
  - Avg_Delivery_Time = AVERAGE(Fact_Livraison[delai_total_heures]) / 24
  - On_Time_Delivery_% = DIVIDE(
      CALCULATE(COUNT(Fact_Livraison[id_fact_livraison]), 
                Fact_Livraison[is_livraison_ontime] = TRUE),
      COUNT(Fact_Livraison[id_fact_livraison])
    )
  - Total_Deliveries = COUNT(Fact_Livraison[id_fact_livraison])


-- ===========================================================================
-- MODULE 5: CUSTOMER SATISFACTION
-- ===========================================================================

-- -------------------------
-- Dim_Satisfaction_Category (NEW)
-- -------------------------
TABLE: Dim_Satisfaction_Category
Primary Key: id_satisfaction_category
Columns:
  - id_satisfaction_category (INT) [PK]
  - category_name (VARCHAR) -- Product Quality, Delivery, Service, Value
  - category_description (TEXT)
  - weight (DECIMAL) -- For weighted NPS calculation
  - display_order (INT)

-- -------------------------
-- FACT_Satisfaction (Satisfaction Fact Table) - ENHANCED
-- -------------------------
TABLE: Fact_Satisfaction
Primary Key: id_satisfaction
Grain: One row per customer review/rating
Columns:
  -- Keys
  - id_satisfaction (BIGINT) [PK]
  - id_temps (INT) [FK] → Dim_Temps
  - id_canal (INT) [FK] → Dim_Canal
  - id_client (INT) [FK] → Dim_Client
  - id_produit (INT) [FK] → Dim_Produit
  - id_satisfaction_category (INT) [FK] → Dim_Satisfaction_Category
  
  -- Measures
  - note_satisfaction (INT) -- 1-5 stars
  - taux_satisfaction (DECIMAL) -- 0.0 to 1.0
  - nombre_avis (INT)
  - nombre_ventes (INT)
  
  -- NEW: Enhanced Metrics
  - nps_score (INT) -- Net Promoter Score: -100 to 100
  - nps_category (VARCHAR) -- Promoter (9-10), Passive (7-8), Detractor (0-6)
  - sentiment_score (DECIMAL) -- -1.0 (negative) to 1.0 (positive)
  - sentiment_label (VARCHAR) -- Positive, Neutral, Negative
  - is_verified_purchase (BOOLEAN)
  - helpful_votes (INT)
  - resolution_time_hours (DECIMAL) -- For complaints
  
  -- Text Data
  - commentaire_text (TEXT)
  - commentaire_langue (VARCHAR)
  
  -- Degenerate Dimensions
  - order_id (VARCHAR)
  - review_id (VARCHAR)
  - review_source (VARCHAR) -- Website, Email Survey, Phone, etc.
  
  -- Timestamps
  - date_review (DATETIME)

Indexes:
  - idx_satisfaction_temps ON (id_temps)
  - idx_satisfaction_produit ON (id_produit)
  - idx_satisfaction_client ON (id_client)

Power BI Measures (DAX):
  - Avg_Rating = AVERAGE(Fact_Satisfaction[note_satisfaction])
  - NPS = (Promoters% - Detractors%) * 100
  - CSAT_Score = AVERAGE(Fact_Satisfaction[taux_satisfaction]) * 100
  - Total_Reviews = COUNT(Fact_Satisfaction[id_satisfaction])
  - Positive_Sentiment_% = DIVIDE(
      CALCULATE(COUNT(Fact_Satisfaction[id_satisfaction]),
                Fact_Satisfaction[sentiment_label] = "Positive"),
      COUNT(Fact_Satisfaction[id_satisfaction])
    )


-- ===========================================================================
-- RELATIONSHIPS DIAGRAM
-- ===========================================================================

Star Schema Relationships (One-to-Many):

Dim_Temps (1) ────────→ (*) Fact_Vente
Dim_Temps (1) ────────→ (*) Fact_Livraison
Dim_Temps (1) ────────→ (*) Fact_Satisfaction
Dim_Temps (1) ────────→ (*) Fact_Daily_Sales

Dim_Client (1) ───────→ (*) Fact_Vente
Dim_Client (1) ───────→ (*) Fact_Livraison
Dim_Client (1) ───────→ (*) Fact_Satisfaction

Dim_Produit (1) ──────→ (*) Fact_Vente
Dim_Produit (1) ──────→ (*) Fact_Satisfaction

Dim_Canal (1) ────────→ (*) Fact_Vente
Dim_Canal (1) ────────→ (*) Fact_Satisfaction
Dim_Canal (1) ────────→ (*) Fact_Daily_Sales

Dim_Region (1) ───────→ (*) Fact_Vente
Dim_Region (1) ───────→ (*) Fact_Livraison
Dim_Region (1) ───────→ (*) Fact_Daily_Sales

Dim_Livraison (1) ────→ (*) Fact_Livraison

Dim_Order_Status (1) ─→ (*) Fact_Livraison

Dim_Customer_Segment (1) → (*) Fact_Vente

Dim_Satisfaction_Category (1) → (*) Fact_Satisfaction

Snowflake Relationships:

Dim_Client (1) ───────→ (*) Dim_Region
Dim_Produit (1) ──────→ (*) Distribution_Centers
Dim_Produit (1) ──────→ (*) Dim_Product_Category (optional)


-- ===========================================================================
-- POWER BI SPECIFIC CONFIGURATIONS
-- ===========================================================================

-- Date Table Configuration:
-- 1. Mark Dim_Temps as Date Table
-- 2. Set date_complete as Date column
-- 3. Hide technical columns (id_temps) from report view
-- 4. Create hierarchies: Year > Quarter > Month > Date

-- Relationship Cardinality:
-- - All Dimension → Fact: One-to-Many (1:*)
-- - Direction: Single (from Dimension to Fact)
-- - Cross-filter: Single direction for performance

-- Performance Optimization:
-- 1. Use import mode for dimensions (< 1M rows)
-- 2. Consider DirectQuery/Composite for large facts
-- 3. Create aggregation tables for common queries
-- 4. Remove unused columns from data model
-- 5. Set appropriate data types (reduce column size)

-- Security:
-- - Row-level security on Dim_Region for regional managers
-- - Role-based access on Dim_Canal for channel managers
-- - Customer data masking for PII compliance


-- ===========================================================================
-- INDEXES SUMMARY FOR PERFORMANCE
-- ===========================================================================

Critical Indexes:
  1. All Primary Keys (automatic)
  2. All Foreign Keys in Fact tables
  3. Date columns in all tables
  4. Frequently filtered columns (status, category, region)
  5. Columns used in joins

Composite Indexes:
  - Fact_Vente: (id_temps, id_client, id_produit)
  - Fact_Livraison: (id_temps, id_region, id_status)
  - Dim_Client: (ville, province, pays)


-- ===========================================================================
-- DATA QUALITY RULES
-- ===========================================================================

Validation Rules:
  1. All foreign keys must have matching dimension records
  2. Dates in facts must exist in Dim_Temps
  3. No negative quantities or prices
  4. Revenue >= Cost (profit can't exceed 100% margin)
  5. Delivery dates: shipped <= delivered
  6. Ratings: 1-5 range only
  7. NPS: 0-10 range only

Default Values:
  - Unknown customer: id_client = -1
  - Unknown product: id_produit = -1
  - Missing date: id_temps = -1 (1900-01-01)

/*******************************************************************************
 * END OF SCHEMA DEFINITION
 ******************************************************************************/
