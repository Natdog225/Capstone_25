"""
Historical Comparison Service
Compare current metrics with past performance
"""

import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from pathlib import Path

logger = logging.getLogger(__name__)


class HistoricalService:
    """
    Service for historical data comparison and trend analysis

    Features:
    - Compare today vs same day last week
    - Compare today vs same day last year
    - Calculate trends and changes
    - Provide insights
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.processed_dir = self.data_dir / "processed"

        # Load historical data
        self._load_historical_data()

        logger.info("Historical Service initialized")

    def _load_historical_data(self):
        """Load historical data from processed files"""
        try:
            # Load orders
            orders_file = self.processed_dir / "orders_from_real_data.csv"
            if orders_file.exists():
                self.orders = pd.read_csv(orders_file)
                self.orders["order_timestamp"] = pd.to_datetime(
                    self.orders["order_timestamp"]
                )
                self.orders["date"] = self.orders["order_timestamp"].dt.date
                logger.info(f"✓ Loaded {len(self.orders)} historical orders")
            else:
                logger.warning("No historical orders data found")
                self.orders = pd.DataFrame()

            # Load wait times (if available)
            wait_times_file = self.processed_dir / "wait_times_from_real_data.csv"
            if wait_times_file.exists():
                self.wait_times = pd.read_csv(wait_times_file)
                time_col = (
                    "log_timestamp"
                    if "log_timestamp" in self.wait_times.columns
                    else "timestamp_quoted"
                )
                self.wait_times[time_col] = pd.to_datetime(self.wait_times[time_col])
                self.wait_times["date"] = self.wait_times[time_col].dt.date
                logger.info(f"✓ Loaded {len(self.wait_times)} historical wait times")
            else:
                logger.warning("No historical wait times data found")
                self.wait_times = pd.DataFrame()

        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            self.orders = pd.DataFrame()
            self.wait_times = pd.DataFrame()

    def get_same_day_last_week(self, reference_date: datetime = None) -> datetime:
        """
        Get the date for the same day last week

        Args:
            reference_date: Reference date (default: today)

        Returns:
            datetime: Date one week ago
        """
        if reference_date is None:
            reference_date = datetime.now()
        return reference_date - timedelta(days=7)

    def get_same_day_last_year(self, reference_date: datetime = None) -> datetime:
        """
        Get the date for the same day last year

        Args:
            reference_date: Reference date (default: today)

        Returns:
            datetime: Date one year ago
        """
        if reference_date is None:
            reference_date = datetime.now()
        try:
            return reference_date.replace(year=reference_date.year - 1)
        except ValueError:
            # Handle leap year edge case (Feb 29)
            return reference_date.replace(year=reference_date.year - 1, day=28)

    def compare_wait_times(self, reference_date: datetime = None) -> Dict:
        """
        Compare today's wait times with historical data

        Args:
            reference_date: Reference date (default: today)

        Returns:
            dict: Comparison data
        """
        if self.wait_times.empty:
            return {"error": "No historical wait time data available"}

        if reference_date is None:
            reference_date = datetime.now()

        today = reference_date.date()
        last_week = self.get_same_day_last_week(reference_date).date()
        last_year = self.get_same_day_last_year(reference_date).date()

        # Get wait times for each period
        today_data = self.wait_times[self.wait_times["date"] == today]
        last_week_data = self.wait_times[self.wait_times["date"] == last_week]
        last_year_data = self.wait_times[self.wait_times["date"] == last_year]

        # Calculate averages
        if "actual_wait_minutes" in self.wait_times.columns:
            wait_col = "actual_wait_minutes"
        else:
            wait_col = self.wait_times.columns[
                self.wait_times.columns.str.contains("wait", case=False)
            ][0]

        today_avg = today_data[wait_col].mean() if len(today_data) > 0 else None
        last_week_avg = (
            last_week_data[wait_col].mean() if len(last_week_data) > 0 else None
        )
        last_year_avg = (
            last_year_data[wait_col].mean() if len(last_year_data) > 0 else None
        )

        # Calculate changes
        comparison = {
            "metric": "wait_time",
            "today": {
                "date": today.isoformat(),
                "average_minutes": round(today_avg, 1) if today_avg else None,
                "count": len(today_data),
            },
            "last_week": {
                "date": last_week.isoformat(),
                "average_minutes": round(last_week_avg, 1) if last_week_avg else None,
                "count": len(last_week_data),
                "change_percent": (
                    self._calculate_change_percent(today_avg, last_week_avg)
                    if today_avg and last_week_avg
                    else None
                ),
                "change_minutes": (
                    round(today_avg - last_week_avg, 1)
                    if today_avg and last_week_avg
                    else None
                ),
            },
            "last_year": {
                "date": last_year.isoformat(),
                "average_minutes": round(last_year_avg, 1) if last_year_avg else None,
                "count": len(last_year_data),
                "change_percent": (
                    self._calculate_change_percent(today_avg, last_year_avg)
                    if today_avg and last_year_avg
                    else None
                ),
                "change_minutes": (
                    round(today_avg - last_year_avg, 1)
                    if today_avg and last_year_avg
                    else None
                ),
            },
            "insight": self._generate_wait_time_insight(
                today_avg, last_week_avg, last_year_avg
            ),
        }

        return comparison

    def compare_sales(self, reference_date: datetime = None) -> Dict:
        """
        Compare today's sales with historical data

        Args:
            reference_date: Reference date (default: today)

        Returns:
            dict: Comparison data
        """
        if self.orders.empty:
            return {"error": "No historical sales data available"}

        if reference_date is None:
            reference_date = datetime.now()

        today = reference_date.date()
        last_week = self.get_same_day_last_week(reference_date).date()
        last_year = self.get_same_day_last_year(reference_date).date()

        # Get sales for each period
        today_sales = self.orders[self.orders["date"] == today]["order_total"].sum()
        last_week_sales = self.orders[self.orders["date"] == last_week][
            "order_total"
        ].sum()
        last_year_sales = self.orders[self.orders["date"] == last_year][
            "order_total"
        ].sum()

        # Get order counts
        today_count = len(self.orders[self.orders["date"] == today])
        last_week_count = len(self.orders[self.orders["date"] == last_week])
        last_year_count = len(self.orders[self.orders["date"] == last_year])

        comparison = {
            "metric": "sales",
            "today": {
                "date": today.isoformat(),
                "total": round(today_sales, 2),
                "order_count": today_count,
                "average_order": (
                    round(today_sales / today_count, 2) if today_count > 0 else 0
                ),
            },
            "last_week": {
                "date": last_week.isoformat(),
                "total": round(last_week_sales, 2),
                "order_count": last_week_count,
                "average_order": (
                    round(last_week_sales / last_week_count, 2)
                    if last_week_count > 0
                    else 0
                ),
                "change_percent": self._calculate_change_percent(
                    today_sales, last_week_sales
                ),
                "change_amount": round(today_sales - last_week_sales, 2),
            },
            "last_year": {
                "date": last_year.isoformat(),
                "total": round(last_year_sales, 2),
                "order_count": last_year_count,
                "average_order": (
                    round(last_year_sales / last_year_count, 2)
                    if last_year_count > 0
                    else 0
                ),
                "change_percent": self._calculate_change_percent(
                    today_sales, last_year_sales
                ),
                "change_amount": round(today_sales - last_year_sales, 2),
            },
            "insight": self._generate_sales_insight(
                today_sales, last_week_sales, last_year_sales
            ),
        }

        return comparison

    def compare_busyness(self, reference_date: datetime = None) -> Dict:
        """
        Compare today's busyness with historical data

        Args:
            reference_date: Reference date (default: today)

        Returns:
            dict: Comparison data
        """
        if self.orders.empty:
            return {"error": "No historical order data available"}

        if reference_date is None:
            reference_date = datetime.now()

        today = reference_date.date()
        last_week = self.get_same_day_last_week(reference_date).date()
        last_year = self.get_same_day_last_year(reference_date).date()

        # Count orders per hour for each period
        today_orders = len(self.orders[self.orders["date"] == today])
        last_week_orders = len(self.orders[self.orders["date"] == last_week])
        last_year_orders = len(self.orders[self.orders["date"] == last_year])

        # Calculate busyness score (orders per hour)
        # Assume 12 hour operating day
        today_busyness = today_orders / 12 if today_orders > 0 else 0
        last_week_busyness = last_week_orders / 12 if last_week_orders > 0 else 0
        last_year_busyness = last_year_orders / 12 if last_year_orders > 0 else 0

        comparison = {
            "metric": "busyness",
            "today": {
                "date": today.isoformat(),
                "total_orders": today_orders,
                "orders_per_hour": round(today_busyness, 1),
            },
            "last_week": {
                "date": last_week.isoformat(),
                "total_orders": last_week_orders,
                "orders_per_hour": round(last_week_busyness, 1),
                "change_percent": self._calculate_change_percent(
                    today_orders, last_week_orders
                ),
                "change_orders": today_orders - last_week_orders,
            },
            "last_year": {
                "date": last_year.isoformat(),
                "total_orders": last_year_orders,
                "orders_per_hour": round(last_year_busyness, 1),
                "change_percent": self._calculate_change_percent(
                    today_orders, last_year_orders
                ),
                "change_orders": today_orders - last_year_orders,
            },
            "insight": self._generate_busyness_insight(
                today_orders, last_week_orders, last_year_orders
            ),
        }

        return comparison

    def get_weekly_trend(self, weeks: int = 4) -> Dict:
        """
        Get weekly trend data for the past N weeks

        Args:
            weeks: Number of weeks to analyze

        Returns:
            dict: Weekly trend data
        """
        if self.orders.empty:
            return {"error": "No historical data available"}

        end_date = datetime.now().date()
        start_date = end_date - timedelta(weeks=weeks)

        # Filter data
        period_orders = self.orders[
            (self.orders["date"] >= start_date) & (self.orders["date"] <= end_date)
        ]

        # Group by week
        period_orders["week"] = (
            pd.to_datetime(period_orders["date"]).dt.isocalendar().week
        )
        period_orders["year"] = pd.to_datetime(period_orders["date"]).dt.year

        weekly_stats = (
            period_orders.groupby(["year", "week"])
            .agg({"order_total": "sum", "order_id": "count"})
            .reset_index()
        )

        weekly_stats.columns = ["year", "week", "sales", "order_count"]

        return {
            "period": f"Last {weeks} weeks",
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "weekly_data": weekly_stats.to_dict("records"),
        }

    def _calculate_change_percent(
        self, current: float, previous: float
    ) -> Optional[float]:
        """Calculate percent change"""
        if previous == 0 or previous is None or current is None:
            return None
        return round(((current - previous) / previous) * 100, 1)

    def _generate_wait_time_insight(
        self,
        today: Optional[float],
        last_week: Optional[float],
        last_year: Optional[float],
    ) -> str:
        """Generate insight text for wait time comparison"""
        if today is None:
            return "No wait time data available for today"

        insights = []

        if last_week is not None:
            change = today - last_week
            if change > 5:
                insights.append(
                    f"Wait times are {abs(round(change, 1))} minutes longer than last week"
                )
            elif change < -5:
                insights.append(
                    f"Wait times are {abs(round(change, 1))} minutes shorter than last week"
                )
            else:
                insights.append("Wait times are similar to last week")

        if last_year is not None:
            change = today - last_year
            if abs(change) > 5:
                direction = "longer" if change > 0 else "shorter"
                insights.append(
                    f"{abs(round(change, 1))} minutes {direction} than last year"
                )

        return (
            ". ".join(insights)
            if insights
            else "Insufficient historical data for comparison"
        )

    def _generate_sales_insight(
        self, today: float, last_week: float, last_year: float
    ) -> str:
        """Generate insight text for sales comparison"""
        insights = []

        if last_week > 0:
            change_pct = self._calculate_change_percent(today, last_week)
            if change_pct and abs(change_pct) > 10:
                direction = "up" if change_pct > 0 else "down"
                insights.append(
                    f"Sales are {direction} {abs(change_pct)}% vs last week"
                )

        if last_year > 0:
            change_pct = self._calculate_change_percent(today, last_year)
            if change_pct and abs(change_pct) > 10:
                direction = "higher" if change_pct > 0 else "lower"
                insights.append(f"{abs(change_pct)}% {direction} than last year")

        return ". ".join(insights) if insights else "Sales are relatively stable"

    def _generate_busyness_insight(
        self, today: int, last_week: int, last_year: int
    ) -> str:
        """Generate insight text for busyness comparison"""
        insights = []

        if last_week > 0:
            change_pct = self._calculate_change_percent(today, last_week)
            if change_pct and abs(change_pct) > 15:
                direction = "busier" if change_pct > 0 else "quieter"
                insights.append(
                    f"Restaurant is {direction} than last week ({abs(change_pct)}%)"
                )

        return insights[0] if insights else "Busyness levels are normal"


# Global service instance
_historical_service = None


def get_historical_service() -> HistoricalService:
    """Get or create the global historical service instance"""
    global _historical_service
    if _historical_service is None:
        _historical_service = HistoricalService()
    return _historical_service
