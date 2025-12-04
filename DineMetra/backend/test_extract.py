"""
Test the ETL extraction process
"""

import sys
from pathlib import Path

# Add parent directory to path so we can import etl module
sys.path.insert(0, str(Path(__file__).parent))

from etl.extract import DataExtractor

def test_extraction():
    """Test the extraction process"""
    print("🧪 Testing ETL Extraction...")
    
    # Initialize extractor
    extractor = DataExtractor(data_dir="data")
    
    # Extract all data
    data = extractor.extract_all()
    
    # Verify we got all expected datasets
    expected_datasets = ['orders', 'order_items', 'wait_times', 'external_factors', 'menu_items']
    
    print("\n✅ Extraction Test Results:")
    for dataset in expected_datasets:
        if dataset in data:
            print(f"   ✓ {dataset}: {len(data[dataset])} records")
        else:
            print(f"   ✗ {dataset}: MISSING")
    
    # Quick data preview
    print("\n📊 Sample Data Preview:")
    print("\nOrders (first 3 rows):")
    print(data['orders'].head(3))
    
    print("\nMenu Items (first 5):")
    print(data['menu_items'].head(5))
    
    print("\n🎉 Extraction test complete!")

if __name__ == "__main__":
    test_extraction()