"""
Dinemetra ML Model Training
Trains prediction models for wait times, busyness, and item sales

This script:
1. Loads cleaned data from ETL pipeline
2. Engineers features for ML models
3. Trains and evaluates models
4. Saves trained models to disk

Run: python scripts/train_models.py
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import pickle
import json
import logging

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.ensemble import RandomForestRegressor, RandomForestClassifier, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score, classification_report
from sklearn.preprocessing import StandardScaler

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ModelTrainer:
    """
    Handles training of all Dinemetra prediction models
    """
    
    def __init__(self, data_dir: str = "data", models_dir: str = "models"):
        """
        Initialize trainer
        
        Args:
            data_dir: Directory containing cleaned data
            models_dir: Directory to save trained models
        """
        self.data_dir = Path(data_dir)
        self.models_dir = Path(models_dir)
        self.models_dir.mkdir(exist_ok=True)
        
        self.training_report = {
            'timestamp': datetime.now().isoformat(),
            'models_trained': {},
            'feature_importance': {}
        }
    
    def load_cleaned_data(self) -> dict:
        """Load cleaned data from ETL pipeline"""
        logger.info("📥 Loading cleaned data from ETL...")
        
        # Run ETL pipeline to get cleaned data
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from etl.extract import DataExtractor
        from etl.transform import DataTransformer
        
        extractor = DataExtractor(data_dir=str(self.data_dir))
        raw_data = extractor.extract_all()
        
        transformer = DataTransformer()
        cleaned_data = transformer.transform_all(raw_data)
        
        logger.info("✓ Data loaded successfully")
        return cleaned_data
    
    def train_all_models(self):
        """Train all prediction models"""
        logger.info("🤖 Starting model training pipeline...\n")
        
        # Load data
        data = self.load_cleaned_data()
        
        # Train each model
        logger.info("="*60)
        self.train_wait_time_model(data)
        
        logger.info("\n" + "="*60)
        self.train_busyness_model(data)
        
        logger.info("\n" + "="*60)
        self.train_item_sales_model(data)
        
        # Save training report
        self._save_training_report()
        
        logger.info("\n" + "="*60)
        logger.info("🎉 All models trained successfully!")
        logger.info(f"📁 Models saved to: {self.models_dir}")
    
    # ========================================
    # WAIT TIME PREDICTION MODEL
    # ========================================
    
    def train_wait_time_model(self, data: dict):
        """
        Train wait time prediction model
        
        Features:
        - party_size
        - hour_of_day
        - day_of_week
        - current_table_occupancy_pct
        - is_weekend
        - is_peak_hour
        
        Target: actual_wait_minutes
        """
        logger.info("⏱️  Training Wait Time Prediction Model")
        logger.info("-" * 60)
        
        # Prepare data
        df = data['wait_times'].copy()
        
        # Remove records with missing actual wait times
        df = df[df['actual_wait_minutes'].notna()]
        
        logger.info(f"Training samples: {len(df):,}")
        
        # Feature engineering
        df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
        df['is_peak_hour'] = df['hour_of_day'].isin([11, 12, 13, 17, 18, 19, 20]).astype(int)
        df['is_lunch'] = df['hour_of_day'].isin([11, 12, 13]).astype(int)
        df['is_dinner'] = df['hour_of_day'].isin([17, 18, 19, 20]).astype(int)
        
        # Calculate occupancy categories
        df['occupancy_low'] = (df['current_table_occupancy_pct'] < 50).astype(int)
        df['occupancy_high'] = (df['current_table_occupancy_pct'] >= 75).astype(int)
        
        # Party size categories
        df['party_small'] = (df['party_size'] <= 2).astype(int)
        df['party_large'] = (df['party_size'] >= 6).astype(int)
        
        # Select features
        feature_columns = [
            'party_size',
            'hour_of_day',
            'day_of_week',
            'current_table_occupancy_pct',
            'current_party_count',
            'is_weekend',
            'is_peak_hour',
            'is_lunch',
            'is_dinner',
            'occupancy_low',
            'occupancy_high',
            'party_small',
            'party_large'
        ]
        
        X = df[feature_columns]
        y = df['actual_wait_minutes']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"Training set: {len(X_train):,} samples")
        logger.info(f"Test set: {len(X_test):,} samples")
        
        # Train model
        logger.info("\nTraining Random Forest Regressor...")
        model = RandomForestRegressor(
            n_estimators=100,
            max_depth=15,
            min_samples_split=10,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_rmse = np.sqrt(mean_squared_error(y_train, train_pred))
        test_rmse = np.sqrt(mean_squared_error(y_test, test_pred))
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        logger.info("\n📊 Model Performance:")
        logger.info(f"   Train MAE: {train_mae:.2f} minutes")
        logger.info(f"   Test MAE:  {test_mae:.2f} minutes")
        logger.info(f"   Train RMSE: {train_rmse:.2f} minutes")
        logger.info(f"   Test RMSE:  {test_rmse:.2f} minutes")
        logger.info(f"   Train R²: {train_r2:.3f}")
        logger.info(f"   Test R²:  {test_r2:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n🔝 Top 5 Important Features:")
        for idx, row in feature_importance.head(5).iterrows():
            logger.info(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Save model
        model_path = self.models_dir / "wait_time_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_columns,
                'scaler': None,  # Not using scaling for tree-based models
                'metadata': {
                    'train_mae': train_mae,
                    'test_mae': test_mae,
                    'test_r2': test_r2,
                    'trained_at': datetime.now().isoformat(),
                    'training_samples': len(X_train)
                }
            }, f)
        
        logger.info(f"\n✓ Model saved to: {model_path}")
        
        # Update report
        self.training_report['models_trained']['wait_time'] = {
            'model_type': 'RandomForestRegressor',
            'test_mae': float(test_mae),
            'test_rmse': float(test_rmse),
            'test_r2': float(test_r2),
            'features': feature_columns,
            'training_samples': len(X_train)
        }
        self.training_report['feature_importance']['wait_time'] = feature_importance.to_dict('records')
    
    # ========================================
    # BUSYNESS CLASSIFICATION MODEL
    # ========================================
    
    def train_busyness_model(self, data: dict):
        """
        Train busyness level classification model
        
        Features:
        - hour_of_day
        - day_of_week
        - orders_in_hour
        - avg_party_size
        - is_weekend
        - is_holiday
        
        Target: busyness_level (slow/moderate/peak)
        """
        logger.info("📊 Training Busyness Classification Model")
        logger.info("-" * 60)
        
        # Prepare data - aggregate orders by hour
        orders = data['orders'].copy()
        orders['order_timestamp'] = pd.to_datetime(orders['order_timestamp'])
        orders['date'] = orders['order_timestamp'].dt.date
        orders['hour'] = orders['order_timestamp'].dt.hour
        orders['day_of_week'] = orders['order_timestamp'].dt.dayofweek
        
        # Aggregate by date and hour
        hourly_data = orders.groupby(['date', 'hour', 'day_of_week']).agg({
            'order_id': 'count',
            'party_size': 'mean',
            'order_total': 'sum'
        }).reset_index()
        
        hourly_data.columns = ['date', 'hour', 'day_of_week', 'order_count', 'avg_party_size', 'total_revenue']
        
        logger.info(f"Training samples: {len(hourly_data):,}")
        
        # Create busyness labels based on order count
        # Using percentiles to define levels
        q33 = hourly_data['order_count'].quantile(0.33)
        q66 = hourly_data['order_count'].quantile(0.66)
        
        def classify_busyness(count):
            if count <= q33:
                return 'slow'
            elif count <= q66:
                return 'moderate'
            else:
                return 'peak'
        
        hourly_data['busyness_level'] = hourly_data['order_count'].apply(classify_busyness)
        
        logger.info(f"\nBusyness Level Distribution:")
        logger.info(hourly_data['busyness_level'].value_counts())
        
        # Feature engineering
        hourly_data['is_weekend'] = hourly_data['day_of_week'].isin([5, 6]).astype(int)
        hourly_data['is_lunch'] = hourly_data['hour'].isin([11, 12, 13]).astype(int)
        hourly_data['is_dinner'] = hourly_data['hour'].isin([17, 18, 19, 20]).astype(int)
        hourly_data['is_peak_hour'] = hourly_data['hour'].isin([11, 12, 13, 17, 18, 19, 20]).astype(int)
        
        # Merge with external factors
        external = data['external_factors'].copy()
        external['date'] = pd.to_datetime(external['factor_date']).dt.date
        hourly_data = hourly_data.merge(external[['date', 'is_holiday', 'weather_condition']], 
                                        on='date', how='left')
        hourly_data['is_holiday'] = hourly_data['is_holiday'].fillna(False).astype(int)
        
        # One-hot encode weather (if available)
        if 'weather_condition' in hourly_data.columns:
            weather_dummies = pd.get_dummies(hourly_data['weather_condition'], prefix='weather')
            hourly_data = pd.concat([hourly_data, weather_dummies], axis=1)
            weather_features = list(weather_dummies.columns)
        else:
            weather_features = []
        
        # Select features
        feature_columns = [
            'hour',
            'day_of_week',
            'avg_party_size',
            'is_weekend',
            'is_lunch',
            'is_dinner',
            'is_peak_hour',
            'is_holiday'
        ] + weather_features
        
        X = hourly_data[feature_columns].fillna(0)
        y = hourly_data['busyness_level']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        logger.info(f"\nTraining set: {len(X_train):,} samples")
        logger.info(f"Test set: {len(X_test):,} samples")
        
        # Train model
        logger.info("\nTraining Random Forest Classifier...")
        model = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            min_samples_split=10,
            random_state=42,
            n_jobs=-1
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_acc = model.score(X_train, y_train)
        test_acc = model.score(X_test, y_test)
        
        logger.info(f"\n📊 Model Performance:")
        logger.info(f"   Train Accuracy: {train_acc:.3f}")
        logger.info(f"   Test Accuracy:  {test_acc:.3f}")
        
        # Classification report
        y_pred = model.predict(X_test)
        logger.info(f"\n📈 Classification Report:")
        report = classification_report(y_test, y_pred, output_dict=True)
        for level in ['slow', 'moderate', 'peak']:
            if level in report:
                logger.info(f"   {level.capitalize()}: Precision={report[level]['precision']:.3f}, Recall={report[level]['recall']:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n🔝 Top 5 Important Features:")
        for idx, row in feature_importance.head(5).iterrows():
            logger.info(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Save model
        model_path = self.models_dir / "busyness_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_columns,
                'label_mapping': {'slow': 0, 'moderate': 1, 'peak': 2},
                'metadata': {
                    'test_accuracy': test_acc,
                    'trained_at': datetime.now().isoformat(),
                    'training_samples': len(X_train)
                }
            }, f)
        
        logger.info(f"\n✓ Model saved to: {model_path}")
        
        # Update report
        self.training_report['models_trained']['busyness'] = {
            'model_type': 'RandomForestClassifier',
            'test_accuracy': float(test_acc),
            'features': feature_columns,
            'training_samples': len(X_train)
        }
        self.training_report['feature_importance']['busyness'] = feature_importance.to_dict('records')
    
    # ========================================
    # ITEM SALES FORECASTING MODEL
    # ========================================
    
    def train_item_sales_model(self, data: dict):
        """
        Train item sales forecasting model
        
        Features:
        - day_of_week
        - hour_of_day (if hourly, otherwise daily)
        - is_weekend
        - is_holiday
        - item_category
        - historical_avg_sales
        
        Target: quantity sold
        """
        logger.info("🍔 Training Item Sales Forecasting Model")
        logger.info("-" * 60)
        
        # Prepare data
        orders = data['orders'].copy()
        orders['order_timestamp'] = pd.to_datetime(orders['order_timestamp'])
        orders['date'] = orders['order_timestamp'].dt.date
        orders['day_of_week'] = orders['order_timestamp'].dt.dayofweek
        
        order_items = data['order_items'].copy()
        menu = data['menu_items'].copy()
        
        # Merge to get item categories
        order_items = order_items.merge(
            orders[['order_id', 'date', 'day_of_week', 'order_timestamp']], 
            on='order_id', 
            how='left'
        )
        order_items = order_items.merge(
            menu[['item_name', 'category']], 
            on='item_name', 
            how='left'
        )
        
        # Aggregate by item and date
        daily_sales = order_items.groupby(['item_name', 'category', 'date', 'day_of_week']).agg({
            'quantity': 'sum'
        }).reset_index()
        
        logger.info(f"Training samples: {len(daily_sales):,}")
        
        # Feature engineering
        daily_sales['is_weekend'] = daily_sales['day_of_week'].isin([5, 6]).astype(int)
        
        # Calculate historical average sales per item
        item_avg_sales = daily_sales.groupby('item_name')['quantity'].mean().to_dict()
        daily_sales['historical_avg_sales'] = daily_sales['item_name'].map(item_avg_sales)
        
        # Merge with external factors
        external = data['external_factors'].copy()
        external['date'] = pd.to_datetime(external['factor_date']).dt.date
        daily_sales = daily_sales.merge(
            external[['date', 'is_holiday', 'weather_condition']], 
            on='date', 
            how='left'
        )
        daily_sales['is_holiday'] = daily_sales['is_holiday'].fillna(False).astype(int)
        
        # One-hot encode category
        category_dummies = pd.get_dummies(daily_sales['category'], prefix='category')
        daily_sales = pd.concat([daily_sales, category_dummies], axis=1)
        
        # Select top 10 items for focused model (optional: train per-item models)
        top_items = order_items.groupby('item_name')['quantity'].sum().nlargest(10).index
        daily_sales_top = daily_sales[daily_sales['item_name'].isin(top_items)]
        
        logger.info(f"\nTraining on top 10 items: {len(daily_sales_top):,} samples")
        logger.info(f"Items: {list(top_items)}")
        
        # Select features
        category_features = [col for col in daily_sales_top.columns if col.startswith('category_')]
        feature_columns = [
            'day_of_week',
            'is_weekend',
            'is_holiday',
            'historical_avg_sales'
        ] + category_features
        
        X = daily_sales_top[feature_columns].fillna(0)
        y = daily_sales_top['quantity']
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
        
        logger.info(f"\nTraining set: {len(X_train):,} samples")
        logger.info(f"Test set: {len(X_test):,} samples")
        
        # Train model
        logger.info("\nTraining Gradient Boosting Regressor...")
        model = GradientBoostingRegressor(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        
        model.fit(X_train, y_train)
        
        # Evaluate
        train_pred = model.predict(X_train)
        test_pred = model.predict(X_test)
        
        train_mae = mean_absolute_error(y_train, train_pred)
        test_mae = mean_absolute_error(y_test, test_pred)
        train_r2 = r2_score(y_train, train_pred)
        test_r2 = r2_score(y_test, test_pred)
        
        logger.info(f"\n📊 Model Performance:")
        logger.info(f"   Train MAE: {train_mae:.2f} units")
        logger.info(f"   Test MAE:  {test_mae:.2f} units")
        logger.info(f"   Train R²: {train_r2:.3f}")
        logger.info(f"   Test R²:  {test_r2:.3f}")
        
        # Feature importance
        feature_importance = pd.DataFrame({
            'feature': feature_columns,
            'importance': model.feature_importances_
        }).sort_values('importance', ascending=False)
        
        logger.info("\n🔝 Top 5 Important Features:")
        for idx, row in feature_importance.head(5).iterrows():
            logger.info(f"   {row['feature']}: {row['importance']:.3f}")
        
        # Save model
        model_path = self.models_dir / "item_sales_model.pkl"
        with open(model_path, 'wb') as f:
            pickle.dump({
                'model': model,
                'features': feature_columns,
                'item_avg_sales': item_avg_sales,
                'top_items': list(top_items),
                'metadata': {
                    'test_mae': test_mae,
                    'test_r2': test_r2,
                    'trained_at': datetime.now().isoformat(),
                    'training_samples': len(X_train)
                }
            }, f)
        
        logger.info(f"\n✓ Model saved to: {model_path}")
        
        # Update report
        self.training_report['models_trained']['item_sales'] = {
            'model_type': 'GradientBoostingRegressor',
            'test_mae': float(test_mae),
            'test_r2': float(test_r2),
            'features': feature_columns,
            'training_samples': len(X_train),
            'items_covered': list(top_items)
        }
        self.training_report['feature_importance']['item_sales'] = feature_importance.to_dict('records')
    
    # ========================================
    # REPORTING
    # ========================================
    
    def _save_training_report(self):
        """Save training report to JSON"""
        report_path = self.models_dir / "training_report.json"
        
        with open(report_path, 'w') as f:
            json.dump(self.training_report, f, indent=2)
        
        logger.info(f"\n📄 Training report saved to: {report_path}")


# ========================================
# MAIN EXECUTION
# ========================================

def main():
    """Main training function"""
    try:
        trainer = ModelTrainer(data_dir="data", models_dir="models")
        trainer.train_all_models()
        
    except Exception as e:
        logger.error(f"❌ Training failed: {str(e)}")
        raise


if __name__ == "__main__":
    main()