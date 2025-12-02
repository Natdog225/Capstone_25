"""
Dashboard API - Backwards Compatible Version
Supports both /dashboard and /api/dashboard URLs
"""

from fastapi import APIRouter, HTTPException
import logging

from app.services.dashboard_service import get_dashboard_service

logger = logging.getLogger(__name__)

# New organized router with prefix
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])

# Legacy router without prefix (for backwards compatibility)
legacy_router = APIRouter(tags=["dashboard-legacy"])


# =============================================================================
# SHARED IMPLEMENTATIONS
# =============================================================================


def _get_dashboard_impl():
    """Shared dashboard implementation"""
    service = get_dashboard_service()
    return service.get_complete_dashboard()


def _get_highlights_impl():
    """Shared highlights implementation"""
    service = get_dashboard_service()
    return service.get_highlights()


def _get_sales_chart_impl():
    """Shared sales chart implementation"""
    service = get_dashboard_service()
    return service.get_sales_chart()


def _get_metrics_impl():
    """Shared metrics implementation"""
    service = get_dashboard_service()
    return service.get_metrics_grid()


def _get_info_sections_impl():
    """Shared info sections implementation"""
    service = get_dashboard_service()
    return service.get_info_sections()


# =============================================================================
# NEW ORGANIZED ENDPOINTS (under /api/dashboard)
# =============================================================================


@router.get("/")
async def get_full_dashboard_new():
    """
    Get complete dashboard (NEW URL: /api/dashboard/)

    Returns everything the dashboard needs in one call.
    """
    try:
        return _get_dashboard_impl()
    except Exception as e:
        logger.error(f"Dashboard fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_full_dashboard_alt():
    """
    Get complete dashboard (ALTERNATE: /api/dashboard/dashboard)

    Same as /api/dashboard/ - provided for convenience.
    """
    try:
        return _get_dashboard_impl()
    except Exception as e:
        logger.error(f"Dashboard fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/highlights")
async def get_highlights_new():
    """
    Get dashboard highlights (NEW URL: /api/dashboard/highlights)

    Returns:
    - Upcoming events
    - Current weather
    - Peak days this week
    """
    try:
        return _get_highlights_impl()
    except Exception as e:
        logger.error(f"Highlights fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sales-chart")
async def get_sales_chart_new():
    """
    Get 7-day sales chart (NEW URL: /api/dashboard/sales-chart)

    Returns sales data with predictions for future days.
    """
    try:
        return _get_sales_chart_impl()
    except Exception as e:
        logger.error(f"Sales chart fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/metrics")
async def get_metrics_new():
    """
    Get metrics grid (NEW URL: /api/dashboard/metrics)

    Returns top sellers, KPI summaries, and purchasing estimates.
    """
    try:
        return _get_metrics_impl()
    except Exception as e:
        logger.error(f"Metrics fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info-sections")
async def get_info_sections_new():
    """
    Get info sections (NEW URL: /api/dashboard/info-sections)

    Returns:
    - Events list
    - Weather details
    - Labor recommendations
    - Historical comparisons
    """
    try:
        return _get_info_sections_impl()
    except Exception as e:
        logger.error(f"Info sections fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check_new():
    """Dashboard health check (NEW URL: /api/dashboard/health)"""
    return {"status": "healthy", "service": "dashboard"}


# =============================================================================
# LEGACY ENDPOINTS (OLD URLs - for backwards compatibility)
# =============================================================================


@legacy_router.get("/dashboard")
async def get_full_dashboard_legacy():
    """
    Get complete dashboard (LEGACY URL: /dashboard)

    ⚠️ DEPRECATED: Use /api/dashboard/ or /api/dashboard/dashboard instead
    """
    try:
        return _get_dashboard_impl()
    except Exception as e:
        logger.error(f"Dashboard fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@legacy_router.get("/highlights")
async def get_highlights_legacy():
    """
    Get dashboard highlights (LEGACY URL: /highlights)

    ⚠️ DEPRECATED: Use /api/dashboard/highlights instead
    """
    try:
        return _get_highlights_impl()
    except Exception as e:
        logger.error(f"Highlights fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@legacy_router.get("/sales-chart")
async def get_sales_chart_legacy():
    """
    Get 7-day sales chart (LEGACY URL: /sales-chart)

    ⚠️ DEPRECATED: Use /api/dashboard/sales-chart instead
    """
    try:
        return _get_sales_chart_impl()
    except Exception as e:
        logger.error(f"Sales chart fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@legacy_router.get("/metrics")
async def get_metrics_legacy():
    """
    Get metrics grid (LEGACY URL: /metrics)

    ⚠️ DEPRECATED: Use /api/dashboard/metrics instead
    """
    try:
        return _get_metrics_impl()
    except Exception as e:
        logger.error(f"Metrics fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@legacy_router.get("/info-sections")
async def get_info_sections_legacy():
    """
    Get info sections (LEGACY URL: /info-sections)

    ⚠️ DEPRECATED: Use /api/dashboard/info-sections instead
    """
    try:
        return _get_info_sections_impl()
    except Exception as e:
        logger.error(f"Info sections fetch failed: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
