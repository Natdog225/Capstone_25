"""
ML Service - Updated for Event-Aware Models
Matches features: ['item_encoded', 'cat_encoded', 'price', 'day_of_week', 'month', 
                   'is_weekend', 'has_event', 'event_count', 'event_nearby', 'large_event']
"""

import pickle
import numpy as np
from pathlib import Path
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MLService:
    def __init__(self):
        self.models = {}
        self.load_models()
    
    def load_models(self):
        """Load all ML models"""
        try:
            # Item Sales Model
            sales_path = Path('data/models/item_sales_model.pkl')
            if sales_path.exists():
                with open(sales_path, 'rb') as f:
                    self.models['item_sales'] = pickle.load(f)
                features = self.models['item_sales']['features']
                logger.info(f"✓ Item Sales model loaded ({len(features)} features)")
                logger.info(f"  Features: {features}")
            
            # Busyness Model
            busyness_path = Path('models/busyness_model.pkl')
            if busyness_path.exists():
                with open(busyness_path, 'rb') as f:
                    self.models['busyness'] = pickle.load(f)
                logger.info("✓ Busyness model loaded")
            
            # Wait Time Model
            wait_path = Path('models/wait_time_model.pkl')
            if wait_path.exists():
                with open(wait_path, 'rb') as f:
                    self.models['wait_time'] = pickle.load(f)
                logger.info("✓ Wait time model loaded")
                
        except Exception as e:
            logger.error(f"Error loading models: {e}")
    
    def predict_item_sales(self, item_name: str, category: str, price: float, 
                          target_date: datetime = None):
        """Predict item sales (simplified - no event params needed, we'll use defaults)"""
        
        if 'item_sales' not in self.models:
            logger.warning("Item sales model not loaded")
            return {
                'predicted_quantity': 5,
                'confidence': 0.5,
                'margin': {'low': 3, 'high': 7}
            }
        
        try:
            model_data = self.models['item_sales']
            model = model_data['model']
            le_item = model_data['le_item']
            le_cat = model_data['le_cat']
            features = model_data['features']
            
            if target_date is None:
                target_date = datetime.now()
            
            # Encode item and category
            try:
                item_encoded = le_item.transform([item_name])[0]
            except:
                item_encoded = 0  # Unknown item
            
            try:
                cat_encoded = le_cat.transform([category])[0]
            except:
                cat_encoded = 0  # Unknown category
            
            # Date features
            day_of_week = target_date.weekday()
            month = target_date.month
            is_weekend = 1 if day_of_week >= 5 else 0
            
            # Event features (defaults - no event)
            has_event = 0
            event_count = 0
            event_nearby = 0
            large_event = 0
            
            # Build feature vector in EXACT order
            feature_values = {
                'item_encoded': item_encoded,
                'cat_encoded': cat_encoded,
                'price': price,
                'day_of_week': day_of_week,
                'month': month,
                'is_weekend': is_weekend,
                'has_event': has_event,
                'event_count': event_count,
                'event_nearby': event_nearby,
                'large_event': large_event
            }
            
            # Create array in the order the model expects
            X = np.array([[feature_values[f] for f in features]])
            
            # Predict
            prediction = model.predict(X)[0]
            prediction = max(1, int(round(prediction)))
            
            # Calculate margin
            margin_low = max(1, int(prediction * 0.8))
            margin_high = int(prediction * 1.2)
            
            return {
                'predicted_quantity': prediction,
                'confidence': 0.75,
                'margin': {
                    'low': margin_low,
                    'high': margin_high
                }
            }
            
        except Exception as e:
            logger.error(f"Item sales prediction error: {e}", exc_info=True)
            # Fallback
            return {
                'predicted_quantity': 5,
                'confidence': 0.5,
                'margin': {'low': 3, 'high': 7},
                'error': str(e)
            }
    
    def predict_busyness(self, target_datetime: datetime = None):
        """Predict busyness level"""
        
        if 'busyness' not in self.models:
            return {
                'level': 'moderate',
                'expected_guests': 45,
                'confidence': 0.5,
                'percentage': 45
            }
        
        try:
            if target_datetime is None:
                target_datetime = datetime.now()
            
            model_data = self.models['busyness']
            model = model_data['model']
            features = model_data.get('features', ['hour', 'day', 'month', 'is_weekend'])
            
            # Build features
            feature_values = {
                'hour': target_datetime.hour,
                'day': target_datetime.weekday(),
                'month': target_datetime.month,
                'is_weekend': 1 if target_datetime.weekday() >= 5 else 0,
                'has_event': 0,  # Default
                'large_event': 0  # Default
            }
            
            X = np.array([[feature_values[f] for f in features]])
            
            level_num = int(model.predict(X)[0])
            
            level_map = {0: 'slow', 1: 'moderate', 2: 'peak'}
            level = level_map.get(level_num, 'moderate')
            
            guest_map = {'slow': 25, 'moderate': 45, 'peak': 85}
            expected_guests = guest_map[level]
            
            return {
                'level': level,
                'level_number': level_num,
                'expected_guests': expected_guests,
                'confidence': 0.85,
                'percentage': (expected_guests / 100) * 100
            }
            
        except Exception as e:
            logger.error(f"Busyness prediction error: {e}", exc_info=True)
            return {
                'level': 'moderate',
                'expected_guests': 45,
                'confidence': 0.5
            }
    
    def predict_wait_time(self, party_size: int, current_occupancy: float):
        """Predict wait time"""
        
        if 'wait_time' not in self.models:
            base_wait = 15 + (party_size * 2)
            return {
                'predicted_wait_minutes': base_wait,
                'confidence': 0.5,
                'margin': {'low': base_wait - 5, 'high': base_wait + 5}
            }
        
        try:
            model_data = self.models['wait_time']
            model = model_data['model']
            features = model_data.get('features', [])
            
            now = datetime.now()
            hour = now.hour
            day = now.weekday()
            
            feature_values = {
                'party_size': party_size,
                'hour': hour,
                'day': day,
                'occupancy': current_occupancy,
                'busy_hour': 1 if hour in [18, 19, 20] else 0,
                'high_occ': 1 if current_occupancy > 80 else 0,
                'interaction': party_size * current_occupancy
            }
            
            X = np.array([[feature_values[f] for f in features]])
            
            prediction = model.predict(X)[0]
            prediction = max(5, int(round(prediction)))
            
            return {
                'predicted_wait_minutes': prediction,
                'confidence': 0.70,
                'margin': {
                    'low': max(5, prediction - 5),
                    'high': prediction + 10
                }
            }
            
        except Exception as e:
            logger.error(f"Wait time prediction error: {e}", exc_info=True)
            base_wait = 15 + (party_size * 2)
            return {
                'predicted_wait_minutes': base_wait,
                'confidence': 0.5,
                'margin': {'low': base_wait - 5, 'high': base_wait + 5}
            }


# Singleton instance
ml_service = MLService()
