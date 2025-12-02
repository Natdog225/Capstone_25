"""
Alert Management API
Endpoints for managing alerts and alert rules
"""

from fastapi import APIRouter, Query
from typing import Optional
import logging

from app.services.alert_service import get_alert_service, AlertSeverity

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("/active")
async def get_active_alerts(
    severity: Optional[str] = Query(
        None, description="Filter by severity (info, warning, critical)"
    )
):
    """
    Get all active (unresolved) alerts

    Example:
    ```
    GET /api/alerts/active
    GET /api/alerts/active?severity=critical
    ```
    """
    alert_service = get_alert_service()

    # Validate severity
    severity_filter = None
    if severity:
        try:
            severity_filter = AlertSeverity(severity.lower())
        except ValueError:
            return {
                "success": False,
                "error": f"Invalid severity. Must be one of: info, warning, critical",
            }

    alerts = alert_service.get_active_alerts(severity=severity_filter)

    return {"success": True, "count": len(alerts), "alerts": alerts}


@router.get("/history")
async def get_alert_history(
    hours: int = Query(24, ge=1, le=168, description="Hours back to retrieve (1-168)"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of alerts"),
):
    """
    Get alert history

    Example:
    ```
    GET /api/alerts/history?hours=48&limit=50
    ```
    """
    alert_service = get_alert_service()

    history = alert_service.get_alert_history(hours=hours, limit=limit)

    return {"success": True, "count": len(history), "alerts": history}


@router.post("/acknowledge/{alert_id}")
async def acknowledge_alert(alert_id: str):
    """
    Acknowledge an alert

    Marks the alert as seen/acknowledged by a user

    Example:
    ```
    POST /api/alerts/acknowledge/wait_time_critical_1234567890
    ```
    """
    alert_service = get_alert_service()

    success = alert_service.acknowledge_alert(alert_id)

    if success:
        return {"success": True, "message": f"Alert {alert_id} acknowledged"}
    else:
        return {"success": False, "error": "Alert not found"}


@router.post("/resolve/{alert_id}")
async def resolve_alert(alert_id: str):
    """
    Resolve an alert

    Marks the alert as resolved (issue fixed)

    Example:
    ```
    POST /api/alerts/resolve/wait_time_critical_1234567890
    ```
    """
    alert_service = get_alert_service()

    success = alert_service.resolve_alert(alert_id)

    if success:
        return {"success": True, "message": f"Alert {alert_id} resolved"}
    else:
        return {"success": False, "error": "Alert not found"}


@router.get("/stats")
async def get_alert_stats():
    """
    Get alert statistics

    Returns counts of active alerts by severity and recent activity

    Example:
    ```
    GET /api/alerts/stats
    ```
    """
    alert_service = get_alert_service()

    stats = alert_service.get_alert_stats()

    return {"success": True, "stats": stats}


@router.get("/rules")
async def list_alert_rules():
    """
    List all configured alert rules

    Returns information about all alert rules in the system
    """
    alert_service = get_alert_service()

    rules = []
    for rule in alert_service.rules:
        rules.append(
            {
                "rule_id": rule.rule_id,
                "name": rule.name,
                "type": rule.alert_type,
                "severity": rule.severity,
                "cooldown_minutes": rule.cooldown_minutes,
                "last_triggered": (
                    rule.last_triggered.isoformat() if rule.last_triggered else None
                ),
            }
        )

    return {"success": True, "count": len(rules), "rules": rules}
