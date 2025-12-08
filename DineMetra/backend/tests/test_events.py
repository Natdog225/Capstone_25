from datetime import datetime
from app.services.ml_service import predict_wait_time


def test_thunder_game_impact():
    """Test that Thunder game increases wait times"""

    # Normal Friday night
    normal = predict_wait_time(
        party_size=4,
        timestamp=datetime(2025, 11, 21, 19, 0),  # 7pm Friday
        current_occupancy=70.0,
        external_factors=None,
    )

    # Thunder game night
    with_event = predict_wait_time(
        party_size=4,
        timestamp=datetime(2025, 11, 21, 19, 0),
        current_occupancy=70.0,
        external_factors={
            "event_name": "Thunder vs Lakers",
            "event_type": "sports",
            "event_time": datetime(2025, 11, 21, 19, 30),
            "event_attendance_estimated": 18000,
            "event_distance_miles": 0.8,
            "venue_name": "Paycom Center",
        },
    )

    print(f"Normal Friday: {normal['predicted_wait_minutes']} min")
    print(f"With Thunder game: {with_event['predicted_wait_minutes']} min")
    print(
        f"Impact: +{with_event['predicted_wait_minutes'] - normal['predicted_wait_minutes']} min"
    )

    assert (
        with_event["predicted_wait_minutes"] > normal["predicted_wait_minutes"]
    ), "Event should increase wait time!"


if __name__ == "__main__":
    test_thunder_game_impact()
    print("✓ Event impact working!")
