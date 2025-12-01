"""
Historical Comparison API Endpoints
REST API for accessing historical comparison data
"""

from fastapi import APIRouter, Query
from datetime import datetime
from typing import Optional
import logging

from app.services.historical_service import get_historical_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/historical", tags=["historical"])


@router.get("/compare/wait-times")
async def compare_wait_times(
    date: Optional[str] = Query(
        None, description="Reference date (YYYY-MM-DD), defaults to today"
    )
):
    """
    Compare wait times: today vs last week vs last year

    Returns:
    - Today's average wait time
    - Last week's average with % change
    - Last year's average with % change
    - Smart insight text

    Example:
    ```
    GET /api/historical/compare/wait-times
    GET /api/historical/compare/wait-times?date=2025-03-15
    ```
    """
    historical = get_historical_service()

    # Parse date if provided
    reference_date = None
    if date:
        try:
            reference_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}

    comparison = historical.compare_wait_times(reference_date=reference_date)

    return {
        "success": True,
        "data": comparison,
        "reference_date": date or datetime.now().date().isoformat(),
    }


@router.get("/compare/sales")
async def compare_sales(
    date: Optional[str] = Query(
        None, description="Reference date (YYYY-MM-DD), defaults to today"
    )
):
    """
    Compare sales: today vs last week vs last year

    Returns:
    - Today's total sales and order count
    - Last week's totals with % change
    - Last year's totals with % change
    - Smart insight text

    Example:
    ```
    GET /api/historical/compare/sales
    GET /api/historical/compare/sales?date=2025-03-15
    ```
    """
    historical = get_historical_service()

    # Parse date if provided
    reference_date = None
    if date:
        try:
            reference_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}

    comparison = historical.compare_sales(reference_date=reference_date)

    return {
        "success": True,
        "data": comparison,
        "reference_date": date or datetime.now().date().isoformat(),
    }


@router.get("/compare/busyness")
async def compare_busyness(
    date: Optional[str] = Query(
        None, description="Reference date (YYYY-MM-DD), defaults to today"
    )
):
    """
    Compare busyness: today vs last week vs last year

    Returns:
    - Today's order count and orders per hour
    - Last week's counts with % change
    - Last year's counts with % change
    - Smart insight text

    Example:
    ```
    GET /api/historical/compare/busyness
    GET /api/historical/compare/busyness?date=2025-03-15
    ```
    """
    historical = get_historical_service()

    # Parse date if provided
    reference_date = None
    if date:
        try:
            reference_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}

    comparison = historical.compare_busyness(reference_date=reference_date)

    return {
        "success": True,
        "data": comparison,
        "reference_date": date or datetime.now().date().isoformat(),
    }


@router.get("/compare/all")
async def compare_all_metrics(
    date: Optional[str] = Query(
        None, description="Reference date (YYYY-MM-DD), defaults to today"
    )
):
    """
    Get all comparisons in one call

    Returns wait times, sales, and busyness comparisons together

    Example:
    ```
    GET /api/historical/compare/all
    GET /api/historical/compare/all?date=2025-03-15
    ```
    """
    historical = get_historical_service()

    # Parse date if provided
    reference_date = None
    if date:
        try:
            reference_date = datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            return {"error": "Invalid date format. Use YYYY-MM-DD"}

    return {
        "success": True,
        "reference_date": date or datetime.now().date().isoformat(),
        "comparisons": {
            "wait_times": historical.compare_wait_times(reference_date=reference_date),
            "sales": historical.compare_sales(reference_date=reference_date),
            "busyness": historical.compare_busyness(reference_date=reference_date),
        },
    }


@router.get("/trends/weekly")
async def get_weekly_trends(
    weeks: int = Query(4, ge=1, le=52, description="Number of weeks to analyze (1-52)")
):
    """
    Get weekly trend data

    Returns aggregated data for the past N weeks

    Example:
    ```
    GET /api/historical/trends/weekly
    GET /api/historical/trends/weekly?weeks=8
    ```
    """
    historical = get_historical_service()

    trend = historical.get_weekly_trend(weeks=weeks)

    return {"success": True, "data": trend}


@router.get("/summary")
async def get_historical_summary():
    """
    Get a summary of available historical data

    Returns date ranges and record counts
    """
    historical = get_historical_service()

    summary = {
        "success": True,
        "data": {
            "orders": {
                "total_records": (
                    len(historical.orders) if not historical.orders.empty else 0
                ),
                "date_range": (
                    {
                        "start": (
                            historical.orders["date"].min().isoformat()
                            if not historical.orders.empty
                            else None
                        ),
                        "end": (
                            historical.orders["date"].max().isoformat()
                            if not historical.orders.empty
                            else None
                        ),
                    }
                    if not historical.orders.empty
                    else None
                ),
            },
            "wait_times": {
                "total_records": (
                    len(historical.wait_times) if not historical.wait_times.empty else 0
                ),
                "date_range": (
                    {
                        "start": (
                            historical.wait_times["date"].min().isoformat()
                            if not historical.wait_times.empty
                            else None
                        ),
                        "end": (
                            historical.wait_times["date"].max().isoformat()
                            if not historical.wait_times.empty
                            else None
                        ),
                    }
                    if not historical.wait_times.empty
                    else None
                ),
            },
        },
    }

    return summary
