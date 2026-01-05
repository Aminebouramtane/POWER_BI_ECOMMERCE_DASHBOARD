import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

# Read existing datasets
print("Reading existing datasets...")
users = pd.read_csv('users.csv')
products = pd.read_csv('products.csv')
orders = pd.read_csv('orders.csv')
order_items = pd.read_csv('order_items.csv')
distribution_centers = pd.read_csv('distribution_centers.csv')

# ==================== Dim_Region ====================
print("\nGenerating Dim_Region...")
dim_region = users[['city', 'state', 'country']].drop_duplicates().reset_index(drop=True)
dim_region.columns = ['ville', 'region', 'pays']
dim_region.insert(0, 'id_region', range(1, len(dim_region) + 1))
dim_region.to_csv('Dim_Region.csv', index=False)
print(f"Dim_Region created with {len(dim_region)} rows")

# ==================== Dim_Temps ====================
print("\nGenerating Dim_Temps...")
# Create date range from 2019 to 2026
start_date = datetime(2019, 1, 1)
end_date = datetime(2026, 1, 31)
dates = pd.date_range(start=start_date, end=end_date, freq='D')

dim_temps = pd.DataFrame({
    'id_temps': range(1, len(dates) + 1),
    'jour': dates.day,
    'mois': dates.month,
    'annee': dates.year,
    'date_complete': dates.strftime('%Y-%m-%d')
})
dim_temps.to_csv('Dim_Temps.csv', index=False)
print(f"Dim_Temps created with {len(dim_temps)} rows")

# ==================== Dim_Livraison ====================
print("\nGenerating Dim_Livraison...")
modes_livraison = ['Standard', 'Express', 'Economy', 'Same Day', 'Next Day']
types_livraison = ['Domicile', 'Point Relais', 'Magasin', 'Bureau', 'Consigne']

dim_livraison = []
id_liv = 1
for mode in modes_livraison:
    for type_liv in types_livraison:
        dim_livraison.append({
            'id_livraison': id_liv,
            'mode_livraison': mode,
            'type_livraison': type_liv
        })
        id_liv += 1

dim_livraison = pd.DataFrame(dim_livraison)
dim_livraison.to_csv('Dim_Livraison.csv', index=False)
print(f"Dim_Livraison created with {len(dim_livraison)} rows")

# ==================== Dim_Canal ====================
print("\nGenerating Dim_Canal...")
canaux = [
    {'nom_canal': 'Search', 'type_canal': 'Digital', 'categorie_canal': 'Acquisition', 'plateforme': 'Google Ads', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Email', 'type_canal': 'Digital', 'categorie_canal': 'Retention', 'plateforme': 'Email Marketing', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Organic', 'type_canal': 'Digital', 'categorie_canal': 'Acquisition', 'plateforme': 'SEO', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Display', 'type_canal': 'Digital', 'categorie_canal': 'Acquisition', 'plateforme': 'Display Ads', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Facebook', 'type_canal': 'Social Media', 'categorie_canal': 'Acquisition', 'plateforme': 'Facebook Ads', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Instagram', 'type_canal': 'Social Media', 'categorie_canal': 'Acquisition', 'plateforme': 'Instagram Ads', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Amazon', 'type_canal': 'Marketplace', 'categorie_canal': 'Vente', 'plateforme': 'Amazon', 'marketplace_nom': 'Amazon', 'ville_magasin': 'N/A'},
    {'nom_canal': 'eBay', 'type_canal': 'Marketplace', 'categorie_canal': 'Vente', 'plateforme': 'eBay', 'marketplace_nom': 'eBay', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Site Web Direct', 'type_canal': 'Digital', 'categorie_canal': 'Direct', 'plateforme': 'Site proprietaire', 'marketplace_nom': 'N/A', 'ville_magasin': 'N/A'},
    {'nom_canal': 'Magasin Physique', 'type_canal': 'Retail', 'categorie_canal': 'Direct', 'plateforme': 'N/A', 'marketplace_nom': 'N/A', 'ville_magasin': 'Various'}
]

dim_canal = pd.DataFrame(canaux)
dim_canal.insert(0, 'id_canal', range(1, len(dim_canal) + 1))

# Add aggregated metrics
dim_canal['chiffre_affaires'] = np.random.uniform(100000, 5000000, len(dim_canal))
dim_canal['nombre_transactions'] = np.random.randint(500, 50000, len(dim_canal))

dim_canal.to_csv('Dim_Canal.csv', index=False)
print(f"Dim_Canal created with {len(dim_canal)} rows")

# ==================== Dim_Client ====================
print("\nGenerating Dim_Client...")
dim_client = users.copy()
dim_client = dim_client.rename(columns={
    'id': 'id_client',
    'first_name': 'prenom',
    'last_name': 'nom',
    'age': 'age',
    'gender': 'sexe',
    'state': 'province',
    'street_address': 'adresse',
    'postal_code': 'code_postal',
    'city': 'ville',
    'country': 'pays',
    'traffic_source': 'canal_acquisition',
    'created_at': 'date_inscription'
})

dim_client.to_csv('Dim_Client.csv', index=False)
print(f"Dim_Client created with {len(dim_client)} rows")

# ==================== Dim_Produit ====================
print("\nGenerating Dim_Produit...")
dim_produit = products.copy()
dim_produit = dim_produit.rename(columns={
    'id': 'id_produit',
    'cost': 'prix_achat',
    'category': 'categorie',
    'name': 'designation',
    'brand': 'marque',
    'retail_price': 'prix_vente',
    'sku': 'reference_produit',
    'distribution_center_id': 'id_centre_dist'
})
# Remove department column as it's not in the schema
dim_produit = dim_produit[['id_produit', 'prix_achat', 'categorie', 'designation', 
                            'marque', 'prix_vente', 'reference_produit', 'id_centre_dist']]

dim_produit.to_csv('Dim_Produit.csv', index=False)
print(f"Dim_Produit created with {len(dim_produit)} rows")

# ==================== Fact_Vente ====================
print("\nGenerating Fact_Vente...")
# Parse dates for orders
orders['created_at'] = pd.to_datetime(orders['created_at'], format='mixed')

# Merge order_items with orders to get dates and user info
fact_vente_base = order_items.merge(orders[['order_id', 'user_id', 'created_at']], on='order_id', how='left', suffixes=('_item', '_order'))

# Create mapping dictionaries
date_to_id_temps = dict(zip(dim_temps['date_complete'], dim_temps['id_temps']))
user_city_to_region = users.set_index('id')[['city', 'state', 'country']].to_dict('index')
region_to_id = {}
for idx, row in dim_region.iterrows():
    key = (row['ville'], row['region'], row['pays'])
    region_to_id[key] = row['id_region']

traffic_to_canal = {
    'Search': 1, 'Email': 2, 'Organic': 3, 'Display': 4, 
    'Facebook': 5, 'Instagram': 6
}

# Sample for performance (take first 10000 rows)
fact_vente_sample = fact_vente_base.head(10000).copy()

# Debug: check column names
print(f"Columns in fact_vente_sample: {fact_vente_sample.columns.tolist()}")

fact_vente = []
for idx, row in fact_vente_sample.iterrows():
    # Get date id - check if created_at exists with any suffix
    created_at_col = 'created_at' if 'created_at' in row else ('created_at_order' if 'created_at_order' in row else 'created_at_item')
    date_str = row[created_at_col].strftime('%Y-%m-%d') if pd.notna(row[created_at_col]) else None
    id_temps = date_to_id_temps.get(date_str, 1)
    
    # Get region id - check for user_id with any suffix
    user_id_col = 'user_id' if 'user_id' in row else ('user_id_order' if 'user_id_order' in row else 'user_id_item')
    user_info = user_city_to_region.get(row[user_id_col])
    if user_info:
        region_key = (user_info['city'], user_info['state'], user_info['country'])
        id_region = region_to_id.get(region_key, 1)
    else:
        id_region = 1
    
    # Get canal id (randomly assign for now)
    id_canal = random.randint(1, len(dim_canal))
    
    fact_vente.append({
        'id_vente': len(fact_vente) + 1,
        'id_temps': id_temps,
        'id_region': id_region,
        'id_client': row[user_id_col],
        'id_produit': row['product_id'],
        'id_canal': id_canal,
        'chiffre_affaire': row['sale_price'],
        'quantite_vendue': 1,
        'panier_moyen': row['sale_price'],
        'nombre_ventes': 1
    })

fact_vente = pd.DataFrame(fact_vente)
fact_vente.to_csv('Fact_Vente.csv', index=False)
print(f"Fact_Vente created with {len(fact_vente)} rows")

# ==================== Fact_Livraison ====================
print("\nGenerating Fact_Livraison...")
# Filter orders with delivered or shipped status
delivered_orders = orders[orders['status'].isin(['Complete', 'Shipped'])].head(5000).copy()
delivered_orders['created_at'] = pd.to_datetime(delivered_orders['created_at'], format='mixed')

fact_livraison = []
for idx, row in delivered_orders.iterrows():
    date_str = row['created_at'].strftime('%Y-%m-%d')
    id_temps = date_to_id_temps.get(date_str, 1)
    
    # Get region
    user_info = user_city_to_region.get(row['user_id'])
    if user_info:
        region_key = (user_info['city'], user_info['state'], user_info['country'])
        id_region = region_to_id.get(region_key, 1)
    else:
        id_region = 1
    
    fact_livraison.append({
        'id_fact_livraison': len(fact_livraison) + 1,
        'id_temps': id_temps,
        'id_livraison': random.randint(1, len(dim_livraison)),
        'id_region': id_region,
        'id_client': row['user_id']
    })

fact_livraison = pd.DataFrame(fact_livraison)
fact_livraison.to_csv('Fact_Livraison.csv', index=False)
print(f"Fact_Livraison created with {len(fact_livraison)} rows")

# ==================== Fact_Satisfaction ====================
print("\nGenerating Fact_Satisfaction...")
# Generate satisfaction data based on completed orders
completed_orders = orders[orders['status'] == 'Complete'].head(3000).copy()
completed_orders['created_at'] = pd.to_datetime(completed_orders['created_at'], format='mixed')

# Merge with order items to get products
satisfaction_base = completed_orders.merge(
    order_items[['order_id', 'product_id']].drop_duplicates(), 
    on='order_id', 
    how='left'
).head(3000)

fact_satisfaction = []
for idx, row in satisfaction_base.iterrows():
    date_str = row['created_at'].strftime('%Y-%m-%d')
    id_temps = date_to_id_temps.get(date_str, 1)
    
    id_canal = random.randint(1, len(dim_canal))
    note = random.randint(1, 5)
    
    fact_satisfaction.append({
        'id_satisfaction': len(fact_satisfaction) + 1,
        'id_temps': id_temps,
        'id_canal': id_canal,
        'id_client': row['user_id'],
        'id_produit': row['product_id'] if pd.notna(row['product_id']) else 0,
        'note_satisfaction': note,
        'taux_satisfaction': note / 5.0,
        'nombre_avis': 1,
        'nombre_ventes': 1
    })

fact_satisfaction = pd.DataFrame(fact_satisfaction)
fact_satisfaction.to_csv('Fact_Satisfaction.csv', index=False)
print(f"Fact_Satisfaction created with {len(fact_satisfaction)} rows")

print("\n" + "="*50)
print("All datasets generated successfully!")
print("="*50)
print("\nGenerated files:")
print("- Dim_Region.csv")
print("- Dim_Temps.csv")
print("- Dim_Livraison.csv")
print("- Dim_Canal.csv")
print("- Dim_Client.csv")
print("- Dim_Produit.csv")
print("- Fact_Vente.csv")
print("- Fact_Livraison.csv")
print("- Fact_Satisfaction.csv")
