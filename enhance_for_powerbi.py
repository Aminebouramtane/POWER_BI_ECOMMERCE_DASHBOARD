import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import calendar

# Set random seed
np.random.seed(42)

print("="*70)
print("ENHANCING DATA WAREHOUSE FOR POWER BI")
print("="*70)

# Read existing Dim_Temps
print("\n📅 Enhancing Dim_Temps with calendar attributes...")
dim_temps = pd.read_csv('Dim_Temps.csv')
dim_temps['date_complete'] = pd.to_datetime(dim_temps['date_complete'])

# Add enhanced calendar attributes
dim_temps['nom_jour'] = dim_temps['date_complete'].dt.day_name()
dim_temps['nom_mois'] = dim_temps['date_complete'].dt.month_name()
dim_temps['jour_semaine'] = dim_temps['date_complete'].dt.dayofweek + 1  # 1=Monday
dim_temps['semaine_annee'] = dim_temps['date_complete'].dt.isocalendar().week
dim_temps['jour_annee'] = dim_temps['date_complete'].dt.dayofyear

# Business calendar
dim_temps['trimestre'] = dim_temps['date_complete'].dt.quarter
dim_temps['semestre'] = dim_temps['trimestre'].apply(lambda q: 1 if q <= 2 else 2)
dim_temps['trimestre_label'] = 'Q' + dim_temps['trimestre'].astype(str) + ' ' + dim_temps['annee'].astype(str)
dim_temps['semestre_label'] = 'H' + dim_temps['semestre'].astype(str) + ' ' + dim_temps['annee'].astype(str)

# Fiscal calendar (assuming fiscal year = calendar year)
dim_temps['fiscal_year'] = dim_temps['annee']
dim_temps['fiscal_quarter'] = dim_temps['trimestre']
dim_temps['fiscal_month'] = dim_temps['mois']

# Flags
dim_temps['is_weekend'] = dim_temps['jour_semaine'].isin([6, 7])
dim_temps['is_working_day'] = ~dim_temps['is_weekend']

# Holidays (simplified - major international holidays)
def is_holiday(date):
    # New Year's Day
    if date.month == 1 and date.day == 1:
        return True, "New Year's Day"
    # Christmas
    if date.month == 12 and date.day == 25:
        return True, "Christmas"
    # Independence Day (US)
    if date.month == 7 and date.day == 4:
        return True, "Independence Day"
    return False, None

holiday_info = dim_temps['date_complete'].apply(is_holiday)
dim_temps['is_holiday'] = holiday_info.apply(lambda x: x[0])
dim_temps['holiday_name'] = holiday_info.apply(lambda x: x[1] if x[1] else '')

# Current date flags (as of script run date)
today = datetime.now().date()
dim_temps['is_current_day'] = dim_temps['date_complete'].dt.date == today
dim_temps['is_current_week'] = (dim_temps['date_complete'].dt.isocalendar().week == datetime.now().isocalendar().week) & \
                                 (dim_temps['annee'] == datetime.now().year)
dim_temps['is_current_month'] = (dim_temps['mois'] == datetime.now().month) & \
                                 (dim_temps['annee'] == datetime.now().year)
dim_temps['is_current_quarter'] = (dim_temps['trimestre'] == ((datetime.now().month - 1) // 3 + 1)) & \
                                   (dim_temps['annee'] == datetime.now().year)
dim_temps['is_current_year'] = dim_temps['annee'] == datetime.now().year

# Save enhanced Dim_Temps
dim_temps.to_csv('Dim_Temps_Enhanced.csv', index=False)
print(f"✅ Enhanced Dim_Temps with {len(dim_temps.columns)} columns")
print(f"   New attributes: Calendar, Business, Fiscal, Flags")

# ============================================================================
# Enhance Fact_Vente with calculated metrics
# ============================================================================
print("\n💰 Enhancing Fact_Vente with calculated metrics...")
fact_vente = pd.read_csv('Fact_Vente.csv')
products = pd.read_csv('Dim_Produit.csv')

# Merge to get cost information
fact_vente_enhanced = fact_vente.merge(
    products[['id_produit', 'prix_achat', 'prix_vente']], 
    on='id_produit', 
    how='left'
)

# Calculate metrics
fact_vente_enhanced['prix_achat_total'] = fact_vente_enhanced['prix_achat'] * fact_vente_enhanced['quantite_vendue']
fact_vente_enhanced['marge_brute'] = fact_vente_enhanced['chiffre_affaire'] - fact_vente_enhanced['prix_achat_total']
fact_vente_enhanced['taux_marge'] = (fact_vente_enhanced['marge_brute'] / fact_vente_enhanced['chiffre_affaire'] * 100).fillna(0)

# Add order status (randomly assign for demonstration)
statuses = ['Complete', 'Processing', 'Shipped', 'Cancelled', 'Returned']
weights = [0.7, 0.1, 0.1, 0.05, 0.05]
fact_vente_enhanced['order_status'] = np.random.choice(statuses, size=len(fact_vente_enhanced), p=weights)

# Payment methods
payment_methods = ['Credit Card', 'PayPal', 'Debit Card', 'Bank Transfer']
fact_vente_enhanced['payment_method'] = np.random.choice(payment_methods, size=len(fact_vente_enhanced))

# Discount (random, some orders have discounts)
fact_vente_enhanced['remise_montant'] = np.where(
    np.random.random(len(fact_vente_enhanced)) > 0.7,
    fact_vente_enhanced['chiffre_affaire'] * np.random.uniform(0.05, 0.25, len(fact_vente_enhanced)),
    0
)
fact_vente_enhanced['taux_remise'] = (fact_vente_enhanced['remise_montant'] / fact_vente_enhanced['chiffre_affaire'] * 100).fillna(0)

# Shipping cost
fact_vente_enhanced['cout_livraison'] = np.random.uniform(2, 15, len(fact_vente_enhanced))

# Generate order_id (group by every few rows)
fact_vente_enhanced['order_id'] = 'ORD' + (fact_vente_enhanced.index // 2 + 1000).astype(str)

# Remove temporary merge columns
fact_vente_enhanced = fact_vente_enhanced.drop(columns=['prix_achat', 'prix_vente'])

fact_vente_enhanced.to_csv('Fact_Vente_Enhanced.csv', index=False)
print(f"✅ Enhanced Fact_Vente with {len(fact_vente_enhanced.columns)} columns")
print(f"   New metrics: Margins, Discounts, Costs, Status")

# ============================================================================
# Create Fact_Daily_Sales (Aggregate Table)
# ============================================================================
print("\n📊 Creating Fact_Daily_Sales aggregate table...")
daily_sales = fact_vente_enhanced.groupby(['id_temps', 'id_region', 'id_canal']).agg({
    'chiffre_affaire': 'sum',
    'order_id': 'nunique',
    'quantite_vendue': 'sum',
    'id_client': 'nunique',
    'marge_brute': 'sum'
}).reset_index()

daily_sales.columns = ['id_temps', 'id_region', 'id_canal', 'total_revenue', 
                       'total_orders', 'total_items', 'total_customers', 'total_profit']

daily_sales['avg_order_value'] = daily_sales['total_revenue'] / daily_sales['total_orders']
daily_sales['avg_profit_margin'] = (daily_sales['total_profit'] / daily_sales['total_revenue'] * 100).fillna(0)

daily_sales.to_csv('Fact_Daily_Sales.csv', index=False)
print(f"✅ Created Fact_Daily_Sales with {len(daily_sales)} rows")
print(f"   Grain: Daily by Region and Channel")

# ============================================================================
# Create Dim_Customer_Segment (RFM-based)
# ============================================================================
print("\n👥 Creating Dim_Customer_Segment (RFM analysis)...")
segments = [
    {
        'id_segment': 1,
        'segment_name': 'Champions',
        'segment_description': 'Bought recently, buy often and spend the most',
        'rfm_score': '555',
        'recency_score': 5,
        'frequency_score': 5,
        'monetary_score': 5,
        'min_clv': 10000,
        'max_clv': 999999,
        'is_active': True
    },
    {
        'id_segment': 2,
        'segment_name': 'Loyal Customers',
        'segment_description': 'Spend good money, responsive to promotions',
        'rfm_score': '444',
        'recency_score': 4,
        'frequency_score': 4,
        'monetary_score': 4,
        'min_clv': 5000,
        'max_clv': 9999,
        'is_active': True
    },
    {
        'id_segment': 3,
        'segment_name': 'Potential Loyalists',
        'segment_description': 'Recent customers with average frequency',
        'rfm_score': '543',
        'recency_score': 5,
        'frequency_score': 4,
        'monetary_score': 3,
        'min_clv': 2000,
        'max_clv': 4999,
        'is_active': True
    },
    {
        'id_segment': 4,
        'segment_name': 'New Customers',
        'segment_description': 'Bought recently but not frequently',
        'rfm_score': '511',
        'recency_score': 5,
        'frequency_score': 1,
        'monetary_score': 1,
        'min_clv': 0,
        'max_clv': 999,
        'is_active': True
    },
    {
        'id_segment': 5,
        'segment_name': 'At Risk',
        'segment_description': 'Purchased often but long time ago',
        'rfm_score': '244',
        'recency_score': 2,
        'frequency_score': 4,
        'monetary_score': 4,
        'min_clv': 3000,
        'max_clv': 7999,
        'is_active': True
    },
    {
        'id_segment': 6,
        'segment_name': 'Churned',
        'segment_description': 'Haven\'t purchased in a long time',
        'rfm_score': '111',
        'recency_score': 1,
        'frequency_score': 1,
        'monetary_score': 1,
        'min_clv': 0,
        'max_clv': 1999,
        'is_active': False
    },
    {
        'id_segment': 7,
        'segment_name': 'Promising',
        'segment_description': 'Recent shoppers but haven\'t spent much',
        'rfm_score': '512',
        'recency_score': 5,
        'frequency_score': 1,
        'monetary_score': 2,
        'min_clv': 500,
        'max_clv': 1999,
        'is_active': True
    }
]

dim_customer_segment = pd.DataFrame(segments)
dim_customer_segment.to_csv('Dim_Customer_Segment.csv', index=False)
print(f"✅ Created Dim_Customer_Segment with {len(dim_customer_segment)} segments")

# ============================================================================
# Create Dim_Order_Status
# ============================================================================
print("\n📦 Creating Dim_Order_Status...")
order_statuses = [
    {
        'id_status': 1,
        'status_name': 'Complete',
        'status_category': 'Success',
        'is_successful': True,
        'is_cancelled': False,
        'is_returned': False,
        'display_color': '#28a745',
        'display_order': 1
    },
    {
        'id_status': 2,
        'status_name': 'Shipped',
        'status_category': 'In Progress',
        'is_successful': False,
        'is_cancelled': False,
        'is_returned': False,
        'display_color': '#007bff',
        'display_order': 2
    },
    {
        'id_status': 3,
        'status_name': 'Processing',
        'status_category': 'In Progress',
        'is_successful': False,
        'is_cancelled': False,
        'is_returned': False,
        'display_color': '#ffc107',
        'display_order': 3
    },
    {
        'id_status': 4,
        'status_name': 'Cancelled',
        'status_category': 'Failed',
        'is_successful': False,
        'is_cancelled': True,
        'is_returned': False,
        'display_color': '#dc3545',
        'display_order': 4
    },
    {
        'id_status': 5,
        'status_name': 'Returned',
        'status_category': 'Failed',
        'is_successful': False,
        'is_cancelled': False,
        'is_returned': True,
        'display_color': '#fd7e14',
        'display_order': 5
    }
]

dim_order_status = pd.DataFrame(order_statuses)
dim_order_status.to_csv('Dim_Order_Status.csv', index=False)
print(f"✅ Created Dim_Order_Status with {len(dim_order_status)} statuses")

# ============================================================================
# Enhance Fact_Livraison
# ============================================================================
print("\n🚚 Enhancing Fact_Livraison with calculated metrics...")
fact_livraison = pd.read_csv('Fact_Livraison.csv')
orders = pd.read_csv('orders.csv')

# Parse dates
orders['created_at'] = pd.to_datetime(orders['created_at'], format='mixed', errors='coerce')
orders['shipped_at'] = pd.to_datetime(orders['shipped_at'], format='mixed', errors='coerce')
orders['delivered_at'] = pd.to_datetime(orders['delivered_at'], format='mixed', errors='coerce')
orders['returned_at'] = pd.to_datetime(orders['returned_at'], format='mixed', errors='coerce')

# Sample orders for fact_livraison
orders_sample = orders[orders['status'].isin(['Complete', 'Shipped'])].head(5000).copy()

# Calculate delivery metrics
orders_sample['delai_traitement_heures'] = (
    (orders_sample['shipped_at'] - orders_sample['created_at']).dt.total_seconds() / 3600
).fillna(0)

orders_sample['delai_livraison_heures'] = (
    (orders_sample['delivered_at'] - orders_sample['shipped_at']).dt.total_seconds() / 3600
).fillna(0)

orders_sample['delai_total_heures'] = (
    (orders_sample['delivered_at'] - orders_sample['created_at']).dt.total_seconds() / 3600
).fillna(0)

# Promised delivery (from Dim_Livraison)
dim_livraison = pd.read_csv('Dim_Livraison.csv')
orders_sample['delai_promis_heures'] = np.random.choice([24, 48, 72, 120, 168], size=len(orders_sample))

orders_sample['delai_vs_promis'] = orders_sample['delai_total_heures'] - orders_sample['delai_promis_heures']
orders_sample['is_livraison_ontime'] = orders_sample['delai_vs_promis'] <= 0
orders_sample['is_livraison_retard'] = orders_sample['delai_vs_promis'] > 0

orders_sample['cout_livraison'] = np.random.uniform(5, 25, len(orders_sample))
orders_sample['nombre_tentatives'] = np.random.choice([1, 1, 1, 2, 3], size=len(orders_sample))

# Map to status
status_map = {'Complete': 1, 'Shipped': 2, 'Processing': 3, 'Cancelled': 4, 'Returned': 5}
orders_sample['id_status'] = orders_sample['status'].map(status_map)

# Create enhanced fact_livraison
fact_livraison_enhanced = fact_livraison.head(len(orders_sample)).copy()
fact_livraison_enhanced['delai_traitement_heures'] = orders_sample['delai_traitement_heures'].values
fact_livraison_enhanced['delai_livraison_heures'] = orders_sample['delai_livraison_heures'].values
fact_livraison_enhanced['delai_total_heures'] = orders_sample['delai_total_heures'].values
fact_livraison_enhanced['delai_vs_promis'] = orders_sample['delai_vs_promis'].values
fact_livraison_enhanced['is_livraison_ontime'] = orders_sample['is_livraison_ontime'].values
fact_livraison_enhanced['is_livraison_retard'] = orders_sample['is_livraison_retard'].values
fact_livraison_enhanced['cout_livraison'] = orders_sample['cout_livraison'].values
fact_livraison_enhanced['nombre_tentatives'] = orders_sample['nombre_tentatives'].values
fact_livraison_enhanced['id_status'] = orders_sample['id_status'].values
fact_livraison_enhanced['order_id'] = 'ORD' + (fact_livraison_enhanced.index + 5000).astype(str)
fact_livraison_enhanced['tracking_number'] = 'TRK' + (fact_livraison_enhanced.index + 10000).astype(str)

fact_livraison_enhanced.to_csv('Fact_Livraison_Enhanced.csv', index=False)
print(f"✅ Enhanced Fact_Livraison with {len(fact_livraison_enhanced.columns)} columns")
print(f"   New metrics: Delivery times, SLA tracking, Costs")

# ============================================================================
# Enhance Fact_Satisfaction
# ============================================================================
print("\n⭐ Enhancing Fact_Satisfaction with NPS and sentiment...")
fact_satisfaction = pd.read_csv('Fact_Satisfaction.csv')

# Calculate NPS category (based on 1-5 scale converted to 0-10)
fact_satisfaction['nps_equivalent'] = (fact_satisfaction['note_satisfaction'] - 1) * 2.5  # Convert 1-5 to 0-10

def get_nps_category(score):
    if score >= 9:
        return 'Promoter'
    elif score >= 7:
        return 'Passive'
    else:
        return 'Detractor'

fact_satisfaction['nps_category'] = fact_satisfaction['nps_equivalent'].apply(get_nps_category)

# Calculate NPS score (-100 to 100)
def calculate_nps_score(note):
    if note >= 4:  # 4-5 stars = Promoter
        return 100
    elif note >= 3:  # 3 stars = Passive
        return 0
    else:  # 1-2 stars = Detractor
        return -100

fact_satisfaction['nps_score'] = fact_satisfaction['note_satisfaction'].apply(calculate_nps_score)

# Sentiment analysis (simplified)
fact_satisfaction['sentiment_score'] = (fact_satisfaction['note_satisfaction'] - 3) / 2  # -1 to 1 scale

def get_sentiment_label(score):
    if score > 0.3:
        return 'Positive'
    elif score < -0.3:
        return 'Negative'
    else:
        return 'Neutral'

fact_satisfaction['sentiment_label'] = fact_satisfaction['sentiment_score'].apply(get_sentiment_label)

# Additional attributes
fact_satisfaction['is_verified_purchase'] = np.random.choice([True, False], size=len(fact_satisfaction), p=[0.8, 0.2])
fact_satisfaction['helpful_votes'] = np.random.poisson(5, size=len(fact_satisfaction))
fact_satisfaction['resolution_time_hours'] = np.where(
    fact_satisfaction['note_satisfaction'] < 3,
    np.random.uniform(1, 48, len(fact_satisfaction)),
    0
)
fact_satisfaction['review_id'] = 'REV' + (fact_satisfaction.index + 1000).astype(str)
fact_satisfaction['review_source'] = np.random.choice(
    ['Website', 'Email Survey', 'Phone', 'Mobile App'],
    size=len(fact_satisfaction),
    p=[0.5, 0.3, 0.1, 0.1]
)

# Add satisfaction category (distribute across categories)
fact_satisfaction['id_satisfaction_category'] = np.random.randint(1, 5, size=len(fact_satisfaction))

fact_satisfaction.to_csv('Fact_Satisfaction_Enhanced.csv', index=False)
print(f"✅ Enhanced Fact_Satisfaction with {len(fact_satisfaction.columns)} columns")
print(f"   New metrics: NPS, Sentiment, Verification, Votes")

# ============================================================================
# Create Dim_Satisfaction_Category
# ============================================================================
print("\n🏆 Creating Dim_Satisfaction_Category...")
satisfaction_categories = [
    {
        'id_satisfaction_category': 1,
        'category_name': 'Product Quality',
        'category_description': 'Rating based on product quality and features',
        'weight': 0.35,
        'display_order': 1
    },
    {
        'id_satisfaction_category': 2,
        'category_name': 'Delivery Speed',
        'category_description': 'Rating based on delivery time and punctuality',
        'weight': 0.25,
        'display_order': 2
    },
    {
        'id_satisfaction_category': 3,
        'category_name': 'Customer Service',
        'category_description': 'Rating based on support and communication',
        'weight': 0.20,
        'display_order': 3
    },
    {
        'id_satisfaction_category': 4,
        'category_name': 'Value for Money',
        'category_description': 'Rating based on price-to-value ratio',
        'weight': 0.20,
        'display_order': 4
    }
]

dim_satisfaction_category = pd.DataFrame(satisfaction_categories)
dim_satisfaction_category.to_csv('Dim_Satisfaction_Category.csv', index=False)
print(f"✅ Created Dim_Satisfaction_Category with {len(dim_satisfaction_category)} categories")

print("\n" + "="*70)
print("✨ DATA WAREHOUSE ENHANCEMENT COMPLETE!")
print("="*70)
print("\n📁 Enhanced/Created Files:")
print("   ✅ Dim_Temps_Enhanced.csv")
print("   ✅ Fact_Vente_Enhanced.csv")
print("   ✅ Fact_Daily_Sales.csv")
print("   ✅ Dim_Customer_Segment.csv")
print("   ✅ Dim_Order_Status.csv")
print("   ✅ Fact_Livraison_Enhanced.csv")
print("   ✅ Fact_Satisfaction_Enhanced.csv")
print("   ✅ Dim_Satisfaction_Category.csv")
print("\n🎯 Ready for Power BI import!")
print("="*70)
