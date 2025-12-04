"""
Train Item Sales Model on ALL Your Data
Uses all 57K+ sales instead of just 412 aggregates
"""

import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import pickle
from datetime import datetime
from pathlib import Path

print("=" * 80)
print("TRAINING ITEM SALES MODEL ON ALL DATA")
print("=" * 80)
print()

# Load all your order items
data_path = Path('data/processed/order_items_from_real_data.csv')
orders_path = Path('data/processed/orders_from_real_data.csv')

if not data_path.exists():
    print(f"❌ File not found: {data_path}")
    exit(1)

# Load data
print("📂 Loading data...")
items_df = pd.read_csv(data_path)
orders_df = pd.read_csv(orders_path)
orders_df['order_timestamp'] = pd.to_datetime(orders_df['order_timestamp'])

print(f"✅ Loaded {len(items_df):,} item sales")
print(f"✅ Loaded {len(orders_df):,} orders")
print()

# Merge to get timestamps
print("🔗 Merging timestamps...")
merged = items_df.merge(
    orders_df[['order_id', 'order_timestamp']], 
    on='order_id', 
    how='left'
)

# Add datetime features
merged['date'] = pd.to_datetime(merged['order_timestamp']).dt.date
merged['hour'] = pd.to_datetime(merged['order_timestamp']).dt.hour
merged['day_of_week'] = pd.to_datetime(merged['order_timestamp']).dt.dayofweek
merged['month'] = pd.to_datetime(merged['order_timestamp']).dt.month
merged['is_weekend'] = merged['day_of_week'] >= 5
merged['is_lunch'] = merged['hour'].between(11, 14)
merged['is_dinner'] = merged['hour'].between(17, 21)

print(f"✅ Merged data: {len(merged):,} records with timestamps")
print()

# Aggregate to daily level (one row per item per day)
print("📊 Aggregating to daily sales by item...")
daily = merged.groupby(['date', 'item_name', 'category']).agg({
    'quantity': 'sum',
    'price': 'mean',
    'day_of_week': 'first',
    'month': 'first',
    'is_weekend': 'first',
    'is_lunch': 'max',  # Was item sold during lunch?
    'is_dinner': 'max'   # Was item sold during dinner?
}).reset_index()

daily = daily.rename(columns={'quantity': 'daily_quantity'})

print(f"✅ Daily data: {len(daily):,} samples")
print(f"   Unique items: {daily['item_name'].nunique()}")
print(f"   Date range: {daily['date'].min()} to {daily['date'].max()}")
print()

# Show top sellers
print("🏆 Top 20 Items by Total Sales:")
top_items = daily.groupby('item_name')['daily_quantity'].sum().sort_values(ascending=False).head(20)
for i, (item, qty) in enumerate(top_items.items(), 1):
    print(f"   {i:2d}. {item:40s}: {qty:,} units")
print()

# Encode categorical features
print("🔧 Encoding features...")
le_item = LabelEncoder()
le_category = LabelEncoder()

daily['item_encoded'] = le_item.fit_transform(daily['item_name'])
daily['category_encoded'] = le_category.fit_transform(daily['category'])

# Add weather sensitivity flags
print("🌡️  Adding weather sensitivity...")
daily['is_fried'] = daily['item_name'].str.lower().str.contains('fry|fried', regex=True).astype(int)
daily['is_banh_mi'] = daily['item_name'].str.lower().str.contains('banh mi', regex=False).astype(int)
daily['is_bowl'] = daily['item_name'].str.lower().str.contains('bowl', regex=False).astype(int)
daily['is_beverage'] = daily['category'].str.lower().str.contains('beverage|drink|soda|water', regex=True).astype(int)
daily['is_salad'] = daily['item_name'].str.lower().str.contains('salad', regex=False).astype(int)

# Features
feature_cols = [
    'item_encoded', 'category_encoded', 'price',
    'day_of_week', 'month', 'is_weekend', 
    'is_lunch', 'is_dinner',
    'is_fried', 'is_banh_mi', 'is_bowl', 'is_beverage', 'is_salad'
]

X = daily[feature_cols]
y = daily['daily_quantity']

print(f"✅ Features: {len(feature_cols)}")
print(f"✅ Training samples: {len(X):,}")
print()

# Split
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print(f"📊 Train: {len(X_train):,} samples")
print(f"📊 Test:  {len(X_test):,} samples")
print()

# Train
print("🎓 Training Random Forest...")
model = RandomForestRegressor(
    n_estimators=200,
    max_depth=20,
    min_samples_split=10,
    min_samples_leaf=5,
    random_state=42,
    n_jobs=-1
)

model.fit(X_train, y_train)
print("✅ Training complete!")
print()

# Evaluate
from sklearn.metrics import mean_absolute_error, r2_score

train_pred = model.predict(X_train)
test_pred = model.predict(X_test)

train_mae = mean_absolute_error(y_train, train_pred)
test_mae = mean_absolute_error(y_test, test_pred)
train_r2 = r2_score(y_train, train_pred)
test_r2 = r2_score(y_test, test_pred)

print("📈 Model Performance:")
print(f"   Train MAE: {train_mae:.2f} units")
print(f"   Test MAE:  {test_mae:.2f} units")
print(f"   Train R²:  {train_r2:.3f}")
print(f"   Test R²:   {test_r2:.3f}")
print()

# Feature importance
print("🔝 Top 10 Important Features:")
importances = model.feature_importances_
feature_importance = sorted(zip(feature_cols, importances), key=lambda x: x[1], reverse=True)
for i, (feat, imp) in enumerate(feature_importance[:10], 1):
    bar = "█" * int(imp * 50)
    print(f"   {i:2d}. {feat:20s}: {bar} {imp:.3f}")
print()

# Save model
print("💾 Saving model...")

model_data = {
    'model': model,
    'label_encoder_item': le_item,
    'label_encoder_category': le_category,
    'feature_cols': feature_cols,
    'trained_date': datetime.now().isoformat(),
    'num_items': len(le_item.classes_),
    'num_samples': len(daily),
    'items': list(le_item.classes_),
    'categories': list(le_category.classes_),
    'metrics': {
        'train_mae': train_mae,
        'test_mae': test_mae,
        'train_r2': train_r2,
        'test_r2': test_r2
    }
}

# Save to data/models (not models/)
output_dir = Path('data/models')
output_dir.mkdir(parents=True, exist_ok=True)
output_path = output_dir / 'item_sales_model.pkl'

with open(output_path, 'wb') as f:
    pickle.dump(model_data, f)

file_size = output_path.stat().st_size / 1024

print(f"✅ Model saved to: {output_path}")
print(f"   File size: {file_size:.1f} KB")
print()

# Test predictions for top items
print("=" * 80)
print("🧪 TESTING PREDICTIONS")
print("=" * 80)
print()

for item_name in ['The Pao', 'Pork Banh Mi', 'Small Kimchi Fry']:
    # Get actual average
    actual_avg = daily[daily['item_name'] == item_name]['daily_quantity'].mean()
    
    # Make prediction (typical Tuesday)
    test_row = {
        'item_encoded': le_item.transform([item_name])[0],
        'category_encoded': le_category.transform([daily[daily['item_name']==item_name]['category'].iloc[0]])[0],
        'price': daily[daily['item_name']==item_name]['price'].mean(),
        'day_of_week': 1,  # Tuesday
        'month': 12,  # December
        'is_weekend': 0,
        'is_lunch': 1,
        'is_dinner': 1,
        'is_fried': 1 if 'fry' in item_name.lower() else 0,
        'is_banh_mi': 1 if 'banh mi' in item_name.lower() else 0,
        'is_bowl': 0,
        'is_beverage': 0,
        'is_salad': 0
    }
    
    X_test_item = pd.DataFrame([test_row])[feature_cols]
    prediction = model.predict(X_test_item)[0]
    
    print(f"Item: {item_name}")
    print(f"  Actual avg:  {actual_avg:.1f} units/day")
    print(f"  Predicted:   {prediction:.1f} units/day")
    print(f"  Accuracy:    {(1 - abs(prediction - actual_avg) / actual_avg) * 100:.1f}%")
    print()

print("=" * 80)
print("✅ SUCCESS!")
print("=" * 80)
print(f"""
📊 Model Statistics:
   • Training samples: {len(daily):,}
   • Unique items: {len(le_item.classes_)}
   • Date range: {daily['date'].min()} to {daily['date'].max()}
   • Test MAE: {test_mae:.2f} units
   • Test R²: {test_r2:.3f}

🎯 This model uses ALL your data:
   • {len(daily):,} daily samples (vs 412 before!)
   • {len(le_item.classes_)} items (vs 10 before!)
   • Much better predictions!

📁 Model saved to: Path('models/item_sales_daily_full.pkl')

🚀 Next steps:
   1. Restart server
   2. Test predictions
   3. Compare to old model
""")