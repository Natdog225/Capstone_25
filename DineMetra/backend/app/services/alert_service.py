"""
Alert Service
Real-time alert system with rule engine and notifications
"""

from typing import Dict, List, Optional
from datetime import datetime, timedelta
from enum import Enum
import logging
import json
from pathlib import Path

logger = logging.getLogger(__name__)


class AlertSeverity(str, Enum):
    """Alert severity levels"""

    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class AlertType(str, Enum):
    """Alert types"""

    WAIT_TIME = "wait_time"
    OCCUPANCY = "occupancy"
    BUSYNESS = "busyness"
    EVENT = "event"
    WEATHER = "weather"
    SALES = "sales"


class Alert:
    """Alert data model"""

    def __init__(
        self,
        alert_id: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        title: str,
        message: str,
        data: Dict,
        triggered_at: datetime,
    ):
        self.alert_id = alert_id
        self.alert_type = alert_type
        self.severity = severity
        self.title = title
        self.message = message
        self.data = data
        self.triggered_at = triggered_at
        self.acknowledged = False
        self.acknowledged_at = None
        self.resolved = False
        self.resolved_at = None

    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            "alert_id": self.alert_id,
            "type": self.alert_type,
            "severity": self.severity,
            "title": self.title,
            "message": self.message,
            "data": self.data,
            "triggered_at": self.triggered_at.isoformat(),
            "acknowledged": self.acknowledged,
            "acknowledged_at": (
                self.acknowledged_at.isoformat() if self.acknowledged_at else None
            ),
            "resolved": self.resolved,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
        }

    def acknowledge(self):
        """Mark alert as acknowledged"""
        self.acknowledged = True
        self.acknowledged_at = datetime.now()

    def resolve(self):
        """Mark alert as resolved"""
        self.resolved = True
        self.resolved_at = datetime.now()


class AlertRule:
    """Alert rule definition"""

    def __init__(
        self,
        rule_id: str,
        name: str,
        alert_type: AlertType,
        severity: AlertSeverity,
        condition_fn,
        message_template: str,
        cooldown_minutes: int = 15,
    ):
        self.rule_id = rule_id
        self.name = name
        self.alert_type = alert_type
        self.severity = severity
        self.condition_fn = condition_fn
        self.message_template = message_template
        self.cooldown_minutes = cooldown_minutes
        self.last_triggered = None

    def should_trigger(self, data: Dict) -> bool:
        """Check if rule should trigger"""
        # Check cooldown
        if self.last_triggered:
            if datetime.now() - self.last_triggered < timedelta(
                minutes=self.cooldown_minutes
            ):
                return False

        # Check condition
        try:
            return self.condition_fn(data)
        except Exception as e:
            logger.error(f"Error checking rule {self.rule_id}: {e}")
            return False

    def trigger(self, data: Dict) -> Alert:
        """Trigger alert"""
        self.last_triggered = datetime.now()

        alert_id = f"{self.rule_id}_{int(datetime.now().timestamp())}"

        # Format message
        message = self.message_template.format(**data)

        alert = Alert(
            alert_id=alert_id,
            alert_type=self.alert_type,
            severity=self.severity,
            title=self.name,
            message=message,
            data=data,
            triggered_at=datetime.now(),
        )

        return alert


class AlertService:
    """
    Alert service with rule engine

    Features:
    - Define alert rules
    - Check conditions
    - Trigger alerts
    - Track alert history
    - Cooldown periods
    """

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.realtime_dir = self.data_dir / "realtime"
        self.realtime_dir.mkdir(parents=True, exist_ok=True)

        # Alert storage
        self.active_alerts: Dict[str, Alert] = {}
        self.alert_history: List[Alert] = []

        # Rules
        self.rules: List[AlertRule] = []

        # Initialize default rules
        self._initialize_default_rules()

        logger.info("Alert Service initialized")

    def _initialize_default_rules(self):
        """Initialize default alert rules"""

        # Critical: Very long wait time
        self.add_rule(
            AlertRule(
                rule_id="wait_time_critical",
                name="Critical Wait Time",
                alert_type=AlertType.WAIT_TIME,
                severity=AlertSeverity.CRITICAL,
                condition_fn=lambda data: data.get("wait_minutes", 0) > 45,
                message_template="Wait time is {wait_minutes} minutes (>{threshold} min threshold)",
                cooldown_minutes=15,
            )
        )

        # Warning: High wait time
        self.add_rule(
            AlertRule(
                rule_id="wait_time_warning",
                name="High Wait Time",
                alert_type=AlertType.WAIT_TIME,
                severity=AlertSeverity.WARNING,
                condition_fn=lambda data: 30 < data.get("wait_minutes", 0) <= 45,
                message_template="Wait time is {wait_minutes} minutes",
                cooldown_minutes=20,
            )
        )

        # Critical: Very high occupancy
        self.add_rule(
            AlertRule(
                rule_id="occupancy_critical",
                name="Critical Occupancy",
                alert_type=AlertType.OCCUPANCY,
                severity=AlertSeverity.CRITICAL,
                condition_fn=lambda data: data.get("occupancy_percent", 0) > 95,
                message_template="Occupancy at {occupancy_percent}% (near capacity)",
                cooldown_minutes=10,
            )
        )

        # Warning: High occupancy
        self.add_rule(
            AlertRule(
                rule_id="occupancy_warning",
                name="High Occupancy",
                alert_type=AlertType.OCCUPANCY,
                severity=AlertSeverity.WARNING,
                condition_fn=lambda data: 85 < data.get("occupancy_percent", 0) <= 95,
                message_template="Occupancy at {occupancy_percent}%",
                cooldown_minutes=15,
            )
        )

        # Info: Nearby event
        self.add_rule(
            AlertRule(
                rule_id="event_nearby",
                name="Nearby Event",
                alert_type=AlertType.EVENT,
                severity=AlertSeverity.INFO,
                condition_fn=lambda data: len(data.get("nearby_events", [])) > 0
                and data.get("event_distance", 999) < 0.5,
                message_template="Event within {event_distance} miles: {event_name}",
                cooldown_minutes=60,
            )
        )

        # Warning: Bad weather
        self.add_rule(
            AlertRule(
                rule_id="weather_warning",
                name="Adverse Weather",
                alert_type=AlertType.WEATHER,
                severity=AlertSeverity.WARNING,
                condition_fn=lambda data: data.get("weather_condition", "")
                in ["stormy", "snowy"]
                or data.get("precipitation_chance", 0) > 70,
                message_template="Weather alert: {weather_condition}, {precipitation_chance}% precipitation",
                cooldown_minutes=120,
            )
        )

        # Info: Peak busyness
        self.add_rule(
            AlertRule(
                rule_id="busyness_peak",
                name="Peak Busyness",
                alert_type=AlertType.BUSYNESS,
                severity=AlertSeverity.INFO,
                condition_fn=lambda data: data.get("busyness_level", "") == "Peak",
                message_template="Restaurant at peak capacity ({expected_guests} expected guests)",
                cooldown_minutes=30,
            )
        )

    def add_rule(self, rule: AlertRule):
        """Add an alert rule"""
        self.rules.append(rule)
        logger.info(f"Added alert rule: {rule.name} ({rule.rule_id})")

    def check_conditions(self, data: Dict) -> List[Alert]:
        """
        Check all rules against current data

        Args:
            data: Current system data to check

        Returns:
            List of triggered alerts
        """
        triggered_alerts = []

        for rule in self.rules:
            if rule.should_trigger(data):
                alert = rule.trigger(data)
                self.active_alerts[alert.alert_id] = alert
                self.alert_history.append(alert)
                triggered_alerts.append(alert)

                logger.warning(f"Alert triggered: {alert.title} - {alert.message}")

        return triggered_alerts

    def get_active_alerts(self, severity: Optional[AlertSeverity] = None) -> List[Dict]:
        """
        Get all active alerts

        Args:
            severity: Optional filter by severity

        Returns:
            List of active alerts
        """
        alerts = [alert for alert in self.active_alerts.values() if not alert.resolved]

        if severity:
            alerts = [alert for alert in alerts if alert.severity == severity]

        return [alert.to_dict() for alert in alerts]

    def get_alert_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """
        Get alert history

        Args:
            hours: Number of hours back to look
            limit: Maximum number of alerts to return

        Returns:
            List of historical alerts
        """
        cutoff_time = datetime.now() - timedelta(hours=hours)

        recent_alerts = [
            alert for alert in self.alert_history if alert.triggered_at >= cutoff_time
        ]

        # Sort by time, most recent first
        recent_alerts.sort(key=lambda x: x.triggered_at, reverse=True)

        return [alert.to_dict() for alert in recent_alerts[:limit]]

    def acknowledge_alert(self, alert_id: str) -> bool:
        """
        Acknowledge an alert

        Args:
            alert_id: Alert ID to acknowledge

        Returns:
            True if acknowledged successfully
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].acknowledge()
            logger.info(f"Alert acknowledged: {alert_id}")
            return True
        return False

    def resolve_alert(self, alert_id: str) -> bool:
        """
        Resolve an alert

        Args:
            alert_id: Alert ID to resolve

        Returns:
            True if resolved successfully
        """
        if alert_id in self.active_alerts:
            self.active_alerts[alert_id].resolve()
            logger.info(f"Alert resolved: {alert_id}")
            return True
        return False

    def get_alert_stats(self) -> Dict:
        """Get alert statistics"""
        active = self.get_active_alerts()

        stats = {
            "active_count": len(active),
            "active_by_severity": {
                "critical": len(
                    [a for a in active if a["severity"] == AlertSeverity.CRITICAL]
                ),
                "warning": len(
                    [a for a in active if a["severity"] == AlertSeverity.WARNING]
                ),
                "info": len([a for a in active if a["severity"] == AlertSeverity.INFO]),
            },
            "total_triggered_24h": len(self.get_alert_history(hours=24)),
            "rules_configured": len(self.rules),
        }

        return stats


# Global service instance
_alert_service = None


def get_alert_service() -> AlertService:
    """Get or create the global alert service instance"""
    global _alert_service
    if _alert_service is None:
        _alert_service = AlertService()
    return _alert_service
