"""
Test trained ML models
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))

from app.services.ml_service import (
    initialize_models,
    predict_wait_time,
    predict_busyness,
    predict_item_sales,
)


def test_wait_time_model():
    """Test wait time predictions"""
    print("⏱️  Testing Wait Time Model")
    print("-" * 60)

    # Test case 1: Small party, lunch time, moderate occupancy
    result = predict_wait_time(
        party_size=2,
        timestamp=datetime(2025, 11, 20, 12, 0),  # Thursday, noon
        current_occupancy=60.0,
    )
    print(f"Small party at lunch (60% occupancy):")
    print(f"  Predicted wait: {result['predicted_wait_minutes']} minutes")
    print(f"  Confidence: {result['confidence']:.2f}")

    # Test case 2: Large party, dinner rush, high occupancy
    result = predict_wait_time(
        party_size=8,
        timestamp=datetime(2025, 11, 22, 19, 0),  # Saturday, 7pm
        current_occupancy=90.0,
    )
    print(f"\nLarge party at Saturday dinner (90% occupancy):")
    print(f"  Predicted wait: {result['predicted_wait_minutes']} minutes")
    print(f"  Confidence: {result['confidence']:.2f}")

    # Test case 3: With event impact
    result = predict_wait_time(
        party_size=4,
        timestamp=datetime(2025, 11, 21, 19, 0),  # Friday, 7pm
        current_occupancy=75.0,
        external_factors={
            "event_name": "Thunder Game",
            "event_type": "sports",
            "event_time": datetime(2025, 11, 21, 19, 30),
            "event_attendance_estimated": 18000,
            "event_distance_miles": 0.8,
        },
    )
    print(f"\nFriday dinner with Thunder game nearby:")
    print(f"  Predicted wait: {result['predicted_wait_minutes']} minutes")
    print(
        f"  Event impact: +{result['factors'].get('event_impact_minutes', 0):.0f} minutes"
    )

    print("\n✓ Wait time model tests complete!\n")


def test_busyness_model():
    """Test busyness predictions"""
    print("📊 Testing Busyness Model")
    print("-" * 60)

    # Test different times
    times = [
        (datetime(2025, 11, 20, 10, 0), "Thursday 10am"),
        (datetime(2025, 11, 20, 12, 0), "Thursday noon"),
        (datetime(2025, 11, 20, 19, 0), "Thursday 7pm"),
        (datetime(2025, 11, 22, 19, 0), "Saturday 7pm"),
    ]

    for timestamp, label in times:
        result = predict_busyness(timestamp)
        print(f"{label}:")
        print(f"  Level: {result['level']}")
        print(f"  Expected guests: {result['expected_guests']}")

    print("\n✓ Busyness model tests complete!\n")


def test_item_sales_model():
    """Test item sales predictions"""
    print("🍔 Testing Item Sales Model")
    print("-" * 60)

    # Test predictions for different days
    dates = [
        (datetime(2025, 11, 20), "Thursday"),  # Weekday
        (datetime(2025, 11, 22), "Saturday"),  # Weekend
    ]

    # Assuming item_id 1 is a popular item
    for date, label in dates:
        result = predict_item_sales(item_id=1, date=date)
        print(f"{label}:")
        print(f"  Predicted quantity: {result['predicted_quantity']}")
        print(f"  Confidence: {result['confidence']:.2f}")

    print("\n✓ Item sales model tests complete!\n")


def main():
    """Run all model tests"""
    print("🧪 Testing Dinemetra ML Models\n")
    print("=" * 60)

    # Initialize models
    initialize_models()

    print("\n" + "=" * 60 + "\n")

    # Run tests
    test_wait_time_model()
    test_busyness_model()
    test_item_sales_model()

    print("=" * 60)
    print("🎉 All model tests complete!")


if __name__ == "__main__":
    main()
