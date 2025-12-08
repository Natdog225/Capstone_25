"""
Quick test script for your ML service
Run this to verify everything works
"""

from app.services.ml_service import predict_wait_time, predict_busyness
from datetime import datetime


def test_wait_time_prediction():
    print("Testing wait time prediction...")

    # Test case 1: Small party, lunch time
    result = predict_wait_time(
        party_size=2, timestamp=datetime(2025, 11, 17, 12, 0), current_occupancy=60.0
    )
    print(f"✓ Small party at lunch: {result['predicted_wait_minutes']} minutes")

    # Test case 2: Large party, dinner rush
    result = predict_wait_time(
        party_size=8, timestamp=datetime(2025, 11, 17, 19, 0), current_occupancy=85.0
    )
    print(f"✓ Large party at dinner: {result['predicted_wait_minutes']} minutes")

    print("\nWait time predictor working! ✓")


def test_busyness_prediction():
    print("\nTesting busyness prediction...")

    result = predict_busyness(timestamp=datetime(2025, 11, 17, 18, 0))
    print(
        f"✓ Dinner time busyness: {result['level']} ({result['expected_guests']} guests)"
    )

    print("\nBusyness predictor working! ✓")


if __name__ == "__main__":
    test_wait_time_prediction()
    test_busyness_prediction()
    print("\n🎉 All ML services operational!")
