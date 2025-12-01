#!/usr/bin/env python3
"""
Quick script to fix the train_models.py weather loading issue
Run this to update your training script
"""

import sys

# Read the current train_models.py
with open('scripts/train_models.py', 'r') as f:
    content = f.read()

# The old code to replace
old_code = '''        # --- FIX 1: Load the ENRICHED data from disk if possible ---
        try:
            df = pd.read_csv("data/processed/wait_times_from_real_data.csv")
            # Check if weather is actually there
            if "weather_condition" not in df.columns:
                raise ValueError("No weather data")
            logger.info("✓ Loaded enriched wait time data with weather history")
        except Exception as e:
            logger.warning(f"⚠️ Could not load enriched data: {e}")
            logger.warning(
                "⚠️ Falling back to standard data (Weather features will be empty!)"
            )
            df = data["wait_times"].copy()'''

# The new code
new_code = '''        # --- FIXED: Load wait times and merge weather from orders ---
        df = None
        
        # Try wait_times file first
        try:
            df = pd.read_csv("data/processed/wait_times_from_real_data.csv")
            if "weather_condition" in df.columns and df["weather_condition"].nunique() > 1:
                logger.info("✓ Loaded enriched wait time data with weather history")
            else:
                df = None
        except:
            pass
        
        # If that didn't work, use standard wait_times and merge weather from orders
        if df is None:
            logger.info("⚠️ Loading wait times, will merge weather from orders...")
            df = data["wait_times"].copy()
            
            # Try to merge weather from orders_from_real_data.csv
            try:
                orders_with_weather = pd.read_csv("data/processed/orders_from_real_data.csv")
                if "weather_condition" in orders_with_weather.columns:
                    # Prepare both dataframes for merge
                    time_col = "log_timestamp" if "log_timestamp" in df.columns else "timestamp_quoted"
                    df[time_col] = pd.to_datetime(df[time_col])
                    df['date'] = df[time_col].dt.date
                    
                    orders_with_weather['order_timestamp'] = pd.to_datetime(orders_with_weather['order_timestamp'])
                    orders_with_weather['date'] = orders_with_weather['order_timestamp'].dt.date
                    
                    # Get unique weather per date
                    weather_by_date = orders_with_weather.groupby('date')['weather_condition'].first().reset_index()
                    
                    # Merge
                    df = df.merge(weather_by_date, on='date', how='left')
                    df['weather_condition'] = df['weather_condition'].fillna('sunny')
                    
                    unique_conditions = df['weather_condition'].nunique()
                    logger.info(f"✓ Merged weather from orders ({unique_conditions} different conditions)")
                    
                    # Show distribution
                    weather_dist = df['weather_condition'].value_counts()
                    logger.info(f"   Weather distribution: {dict(weather_dist)}")
                else:
                    logger.warning("⚠️ No weather in orders file")
                    df['weather_condition'] = 'sunny'
            except Exception as e:
                logger.warning(f"⚠️ Could not merge weather: {e}")
                df['weather_condition'] = 'sunny'''

# Replace
if old_code in content:
    content = content.replace(old_code, new_code)
    
    # Backup original
    with open('scripts/train_models.py.backup', 'w') as f:
        f.write(open('scripts/train_models.py', 'r').read())
    print("✓ Backed up original to scripts/train_models.py.backup")
    
    # Write fixed version
    with open('scripts/train_models.py', 'w') as f:
        f.write(content)
    print("✓ Fixed scripts/train_models.py")
    print("\nNow run: python scripts/train_models.py")
else:
    print("⚠️ Could not find the code to replace")
    print("Your train_models.py might have a different structure")
    print("Manual fix needed - see TRAIN_MODELS_PATCH.txt")
    sys.exit(1)