"""
Historical Comparison Service Test
Tests historical data comparison functionality
"""

import sys

sys.path.insert(0, ".")

from app.services.historical_service import get_historical_service
from datetime import datetime


def test_historical_comparisons():
    print("=" * 60)
    print("HISTORICAL COMPARISONS TEST")
    print("=" * 60)
    print()

    # Get service
    try:
        historical = get_historical_service()
        print("✓ Historical service loaded successfully\n")
    except Exception as e:
        print(f"❌ Failed to load historical service: {e}\n")
        return

    # Use a date from your data range (Jan-Jun 2025)
    test_date = datetime(2025, 3, 15)
    print(f"Testing with date: {test_date.strftime('%Y-%m-%d')}")
    print(f"(Your historical data is from Jan-Jun 2025)\n")

    # Test 1: Wait Times
    print("1. WAIT TIME COMPARISON")
    print("-" * 60)
    try:
        wait_comp = historical.compare_wait_times(reference_date=test_date)

        if "error" in wait_comp:
            print(f"   ⚠️  {wait_comp['error']}")
        else:
            today = wait_comp["today"]
            last_week = wait_comp["last_week"]
            last_year = wait_comp["last_year"]

            print(f"   Today ({test_date.strftime('%Y-%m-%d')}):")
            print(f"      Average: {today.get('average_minutes', 'N/A')} min")
            print(f"      Count: {today.get('count', 0)} records")
            print()
            print(f"   Last Week:")
            print(f"      Average: {last_week.get('average_minutes', 'N/A')} min")
            print(f"      Change: {last_week.get('change_percent', 'N/A')}%")
            print()
            print(f"   Insight: {wait_comp.get('insight', 'N/A')}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
        import traceback

        traceback.print_exc()
    print()

    # Test 2: Sales
    print("2. SALES COMPARISON")
    print("-" * 60)
    try:
        sales_comp = historical.compare_sales(reference_date=test_date)

        if "error" in sales_comp:
            print(f"   ⚠️  {sales_comp['error']}")
        else:
            today = sales_comp["today"]
            last_week = sales_comp["last_week"]

            print(f"   Today ({test_date.strftime('%Y-%m-%d')}):")
            print(f"      Total: ${today['total']:,.2f}")
            print(f"      Orders: {today['order_count']}")
            print()
            print(f"   Last Week:")
            print(f"      Total: ${last_week['total']:,.2f}")
            print(f"      Change: {last_week['change_percent']:+.1f}%")
            print()
            print(f"   Insight: {sales_comp['insight']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Test 3: Busyness
    print("3. BUSYNESS COMPARISON")
    print("-" * 60)
    try:
        busy_comp = historical.compare_busyness(reference_date=test_date)

        if "error" in busy_comp:
            print(f"   ⚠️  {busy_comp['error']}")
        else:
            today = busy_comp["today"]
            last_week = busy_comp["last_week"]

            print(f"   Today ({test_date.strftime('%Y-%m-%d')}):")
            print(f"      Orders: {today['total_orders']}")
            print(f"      Per Hour: {today['orders_per_hour']}")
            print()
            print(f"   Last Week:")
            print(f"      Orders: {last_week['total_orders']}")
            print(f"      Change: {last_week['change_percent']:+.1f}%")
            print()
            print(f"   Insight: {busy_comp['insight']}")

    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    # Test 4: Weekly Trend
    print("4. WEEKLY TREND (Last 4 Weeks from test date)")
    print("-" * 60)
    try:
        # Note: This will calculate 4 weeks back from test_date
        trend = historical.get_weekly_trend(weeks=4)

        if "error" in trend:
            print(f"   ⚠️  {trend['error']}")
        else:
            print(f"   Period: {trend['start_date']} to {trend['end_date']}")
            print(f"   Data points: {len(trend['weekly_data'])}\n")

            if len(trend["weekly_data"]) > 0:
                print("   Week-by-week:")
                for week in trend["weekly_data"]:
                    print(
                        f"   - Week {week['week']}/{week['year']}: ${week['sales']:,.2f} ({week['order_count']} orders)"
                    )
            else:
                print("   No weekly data available")

    except Exception as e:
        print(f"   ❌ Error: {e}")
    print()

    print("=" * 60)
    print("✅ HISTORICAL COMPARISONS TEST COMPLETE")
    print("=" * 60)
    print()
    print("Notes:")
    print("- If today shows 0, that's normal (today is Dec 2025, data is Jan-Jun 2025)")
    print("- Test date (March 15, 2025) should show actual data from your dataset")
    print("- To test current date, wait for more data or use reference_date parameter")


if __name__ == "__main__":
    test_historical_comparisons()
