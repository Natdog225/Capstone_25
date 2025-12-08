"""
Test monitoring and auto-retrain systems
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import json
import random

sys.path.insert(0, str(Path(__file__).parent))

from scripts.monitor_models import ModelMonitor
from scripts.auto_retrain import AutoRetrainer


def generate_fake_prediction_logs():
    """Generate fake prediction logs for testing"""
    monitor = ModelMonitor()

    print("📝 Generating fake prediction logs...")

    # Generate logs for the past 30 days
    for day in range(30):
        date = datetime.now() - timedelta(days=day)

        # Generate 20 wait time predictions per day
        for _ in range(20):
            # Simulate predictions getting worse over time (model drift)
            base_error = 3.0 + (day * 0.1)  # Error increases over time

            predicted = random.uniform(10, 40)
            actual = predicted + random.gauss(0, base_error)

            monitor.log_prediction(
                model_name="wait_time",
                prediction={
                    "predicted_wait_minutes": predicted,
                    "confidence": 0.85,
                    "factors": {},
                },
                actual=max(0, actual),
            )

        # Generate busyness predictions
        for _ in range(15):
            true_level = random.choice(["slow", "moderate", "peak"])
            # Simulate 85% accuracy
            if random.random() < 0.85:
                predicted_level = true_level
            else:
                predicted_level = random.choice(["slow", "moderate", "peak"])

            monitor.log_prediction(
                model_name="busyness",
                prediction={
                    "level": predicted_level,
                    "confidence": 0.75,
                    "expected_guests": 50,
                },
                actual=true_level,
            )

        # Generate item sales predictions
        for _ in range(10):
            predicted_qty = random.uniform(30, 70)
            actual_qty = predicted_qty + random.gauss(0, 8)

            monitor.log_prediction(
                model_name="item_sales",
                prediction={
                    "predicted_quantity": int(predicted_qty),
                    "confidence": 0.70,
                },
                actual=max(0, int(actual_qty)),
            )

    print(f"   ✓ Generated {30 * (20 + 15 + 10)} fake predictions")


def test_monitoring():
    """Test the monitoring system"""
    print("\n" + "=" * 60)
    print("🧪 TESTING MONITORING SYSTEM")
    print("=" * 60)

    monitor = ModelMonitor()

    # Generate report
    report = monitor.generate_monitoring_report(days=30)

    print("\n📊 Monitoring Report Summary:")
    print(f"   Overall Status: {report['overall_status'].upper()}")
    print(f"\n   Model Statuses:")
    for model, metrics in report["models"].items():
        if metrics.get("sample_size", 0) > 0:
            print(
                f"      {model}: {metrics.get('status', 'unknown')} ({metrics['sample_size']} samples)"
            )

    print(f"\n   Recommendations:")
    for rec in report.get("recommendations", []):
        print(f"      {rec}")

    # Generate plots
    try:
        monitor.plot_performance_trends(days=30)
        print("\n   ✓ Performance plots generated")
    except Exception as e:
        print(f"\n   ⚠️  Could not generate plots: {e}")


def test_auto_retrain():
    """Test the auto-retrain system"""
    print("\n" + "=" * 60)
    print("🧪 TESTING AUTO-RETRAIN SYSTEM")
    print("=" * 60)

    retrainer = AutoRetrainer()

    # Check if retrain is needed
    decision = retrainer.should_retrain()

    print(f"\n📊 Retrain Decision:")
    print(f"   Should retrain: {decision['should_retrain']}")
    if decision.get("reasons"):
        print(f"   Reasons:")
        for reason in decision["reasons"]:
            print(f"      - {reason}")

    # Get next scheduled retrain
    next_retrain = retrainer.get_next_scheduled_retrain()
    days_until = (next_retrain - datetime.now()).days
    print(
        f"\n   Next scheduled retrain: {next_retrain.strftime('%Y-%m-%d')} ({days_until} days)"
    )

    print("\n   ℹ️  To test actual retraining, run:")
    print("      python scripts/auto_retrain.py --force")


def main():
    """Run all tests"""
    print("🧪 Testing Dinemetra Monitoring & Auto-Retrain")

    # Check if prediction logs exist
    log_path = Path("logs/predictions.jsonl")
    if not log_path.exists():
        print("\n⚠️  No prediction logs found. Generating fake data for testing...")
        generate_fake_prediction_logs()

    # Test monitoring
    test_monitoring()

    # Test auto-retrain
    test_auto_retrain()

    print("\n" + "=" * 60)
    print("✅ All tests complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
