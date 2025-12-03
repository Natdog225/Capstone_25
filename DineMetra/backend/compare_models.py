"""
Compare Item Sales Models - Which Should You Use?
Run from: /Users/nathan/Repositories/Capstone/Capstone_25/DineMetra/backend
"""

import pickle
from pathlib import Path

print("=" * 80)
print("COMPARING YOUR ITEM SALES MODELS")
print("=" * 80)
print()

# Check all possible locations
models_to_check = [
    ("models/item_sales_daily_full.pkl", "Daily Full (ml_service.py expects this)"),
    ("models/item_sales_monthly.pkl", "Monthly Model"),
    ("data/models/item_sales_model.pkl", "Data Models (test found this)"),
]

results = []

for model_path, description in models_to_check:
    path = Path(model_path)
    if not path.exists():
        print(f"❌ {description}")
        print(f"   NOT FOUND at: {model_path}")
        print()
        continue

    print(f"✅ {description}")
    print(f"   Path: {model_path}")
    print(f"   Size: {path.stat().st_size / 1024:.1f} KB")

    try:
        with open(path, "rb") as f:
            model_data = pickle.load(f)

        if isinstance(model_data, dict):
            num_items = model_data.get("num_items", "N/A")
            num_samples = model_data.get("num_samples", "N/A")

            print(f"   📊 Items: {num_items}")
            print(
                f"   📊 Samples: {num_samples:,}"
                if isinstance(num_samples, int)
                else f"   📊 Samples: {num_samples}"
            )

            # Check for metrics
            if "metrics" in model_data:
                metrics = model_data["metrics"]
                test_mae = metrics.get("test_mae", "N/A")
                test_r2 = metrics.get("test_r2", "N/A")
                print(
                    f"   📈 Test MAE: {test_mae:.2f} units"
                    if isinstance(test_mae, (int, float))
                    else f"   📈 Test MAE: {test_mae}"
                )
                print(
                    f"   📈 Test R²: {test_r2:.3f}"
                    if isinstance(test_r2, (int, float))
                    else f"   📈 Test R²: {test_r2}"
                )

                results.append(
                    {
                        "name": description,
                        "path": model_path,
                        "items": num_items,
                        "samples": num_samples,
                        "mae": test_mae if isinstance(test_mae, (int, float)) else 999,
                        "r2": test_r2 if isinstance(test_r2, (int, float)) else -1,
                    }
                )
            else:
                print(f"   ⚠️ No metrics found (older model format)")
                results.append(
                    {
                        "name": description,
                        "path": model_path,
                        "items": num_items,
                        "samples": num_samples,
                        "mae": 999,
                        "r2": -1,
                    }
                )

            # Show sample items
            if "items" in model_data:
                items_list = model_data["items"]
                print(f"   🍽️  Sample items: {', '.join(items_list[:3])}...")

            # Show training info
            if "months_trained" in model_data:
                print(f"   📅 Trained on: {model_data['months_trained']} months")
            elif "trained_date" in model_data:
                print(f"   📅 Trained: {model_data['trained_date'][:10]}")
        else:
            print(f"   Type: {type(model_data)} (not a dict)")
    except Exception as e:
        print(f"   ⚠️ Error loading: {str(e)[:50]}...")

    print()

# Recommendation
print("=" * 80)
print("🎯 RECOMMENDATION")
print("=" * 80)
print()

if results:
    # Find best model
    best_by_samples = max(
        results, key=lambda x: x["samples"] if isinstance(x["samples"], int) else 0
    )
    best_by_mae = min(results, key=lambda x: x["mae"])

    print("📊 Best by Sample Size:")
    print(f"   {best_by_samples['name']}")
    print(
        f"   {best_by_samples['samples']:,} samples with {best_by_samples['items']} items"
    )
    print()

    print("🎯 Best by Accuracy (lowest MAE):")
    print(f"   {best_by_mae['name']}")
    if best_by_mae["mae"] < 999:
        print(f"   MAE: {best_by_mae['mae']:.2f} units")
    print()

    # Overall recommendation
    print("💡 OVERALL RECOMMENDATION:")
    if best_by_samples == best_by_mae:
        print(f"   ✅ USE: {best_by_samples['path']}")
        print(f"   This model has both the most samples AND best accuracy!")
    else:
        print(f"   ✅ USE: {best_by_mae['path']}")
        print(f"   Better accuracy is more important than sample size.")
    print()

    # Check what ml_service.py expects
    print("⚙️  YOUR ml_service.py EXPECTS:")
    print(f"   models/item_sales_daily_full.pkl")

    expected_path = Path("models/item_sales_daily_full.pkl")
    if not expected_path.exists():
        print()
        print("   ⚠️  This file doesn't exist!")
        print()
        print("   🔧 QUICK FIX:")

        if results:
            best_model = best_by_mae if best_by_mae["mae"] < 999 else best_by_samples
            print(f"   Create a symlink to the best model:")
            print(f"   ln -sf ../{best_model['path']} models/item_sales_daily_full.pkl")
    else:
        print(f"   ✅ File exists - {expected_path.stat().st_size / 1024:.1f} KB")

else:
    print("❌ No models found to compare!")
    print()
    print("💡 You need to train a model first:")
    print("   python scripts/train_model_monthly_folders.py data/real/")

print()
print("=" * 80)
