"""
Background Tasks
Periodic tasks for real-time updates, alerts, and monitoring
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime, timedelta
import logging
import asyncio
from typing import Optional

from app.websocket.manager import get_connection_manager
from app.services.enhanced_prediction_service import enhanced_prediction_service
from app.services.alert_service import get_alert_service
from app.services.ab_testing_service import get_ab_testing_service

logger = logging.getLogger(__name__)


class BackgroundTaskService:
    """
    Background Task Service

    Manages periodic tasks:
    - Broadcast predictions every 5 minutes
    - Check alerts every 1 minute
    - Cleanup old data every hour
    - Monitor system health
    """

    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.connection_manager = get_connection_manager()
        self.prediction_service = get_enhanced_prediction_service()
        self.alert_service = get_alert_service()
        self.ab_testing_service = get_ab_testing_service()

        self.is_running = False

        logger.info("Background Task Service initialized")

    async def broadcast_predictions(self):
        """
        Broadcast latest predictions to all connected clients

        Runs every 5 minutes
        """
        try:
            logger.debug("Broadcasting predictions...")

            # Get current predictions for next hour
            now = datetime.now()

            # Get predictions (simplified - using default input)
            input_data = {
                "hour": now.hour,
                "day_of_week": now.weekday(),
                "is_weekend": now.weekday() >= 5,
                "month": now.month,
            }

            # Get wait time prediction
            wait_time_result = self.prediction_service.predict_wait_time(input_data)

            # Get busyness prediction
            busyness_result = self.prediction_service.predict_busyness(input_data)

            # Prepare broadcast data
            broadcast_data = {
                "type": "prediction_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "wait_time": {
                        "predicted_minutes": wait_time_result["prediction"],
                        "confidence": wait_time_result.get("confidence", 0.85),
                    },
                    "busyness": {
                        "level": busyness_result["prediction"],
                        "confidence": busyness_result.get("confidence", 0.80),
                    },
                },
            }

            # Broadcast to dashboard group
            await self.connection_manager.broadcast_prediction_update(
                broadcast_data["data"]
            )

            logger.info(
                f"Broadcasted predictions to {len(self.connection_manager.get_group_connections('dashboard'))} clients"
            )

        except Exception as e:
            logger.error(f"Error broadcasting predictions: {e}", exc_info=True)

    async def check_alerts(self):
        """
        Check conditions and trigger alerts

        Runs every 1 minute
        """
        try:
            logger.debug("Checking alert conditions...")

            # Get current metrics
            now = datetime.now()

            # Simplified metrics - in production, get real data
            input_data = {
                "hour": now.hour,
                "day_of_week": now.weekday(),
                "is_weekend": now.weekday() >= 5,
                "month": now.month,
            }

            # Get predictions to check against
            wait_time_result = self.prediction_service.predict_wait_time(input_data)
            busyness_result = self.prediction_service.predict_busyness(input_data)

            # Prepare data for alert checking
            alert_data = {
                "wait_minutes": wait_time_result["prediction"],
                "occupancy_percent": 75,  # Would come from real data
                "busyness_level": busyness_result["prediction"],
                "threshold": 45,
                "nearby_events": [],  # Would come from event service
                "event_distance": 999,
                "event_name": "",
                "weather_condition": "sunny",  # Would come from weather service
                "precipitation_chance": 0,
                "expected_guests": 100,
            }

            # Check conditions
            triggered_alerts = self.alert_service.check_conditions(alert_data)

            # Broadcast alerts to connected clients
            for alert in triggered_alerts:
                await self.connection_manager.broadcast_alert(alert.to_dict())
                logger.warning(f"Alert broadcasted: {alert.title}")

            if triggered_alerts:
                logger.info(f"Triggered {len(triggered_alerts)} alerts")

        except Exception as e:
            logger.error(f"Error checking alerts: {e}", exc_info=True)

    async def cleanup_old_data(self):
        """
        Cleanup old data to prevent memory bloat

        Runs every hour
        """
        try:
            logger.debug("Cleaning up old data...")

            # Cleanup old prediction logs (keep last 7 days)
            cutoff_time = datetime.now() - timedelta(days=7)

            before_count = len(self.ab_testing_service.prediction_logs)

            self.ab_testing_service.prediction_logs = [
                log
                for log in self.ab_testing_service.prediction_logs
                if log.timestamp >= cutoff_time
            ]

            after_count = len(self.ab_testing_service.prediction_logs)
            removed = before_count - after_count

            if removed > 0:
                logger.info(f"Cleaned up {removed} old prediction logs")

            # Cleanup resolved alerts (keep last 24 hours)
            alert_cutoff = datetime.now() - timedelta(hours=24)

            before_count = len(self.alert_service.alert_history)

            self.alert_service.alert_history = [
                alert
                for alert in self.alert_service.alert_history
                if alert.triggered_at >= alert_cutoff or not alert.resolved
            ]

            after_count = len(self.alert_service.alert_history)
            removed = before_count - after_count

            if removed > 0:
                logger.info(f"Cleaned up {removed} old alerts")

        except Exception as e:
            logger.error(f"Error cleaning up data: {e}", exc_info=True)

    async def monitor_system_health(self):
        """
        Monitor system health and log stats

        Runs every 15 minutes
        """
        try:
            logger.debug("Monitoring system health...")

            # Connection stats
            conn_stats = self.connection_manager.get_connection_stats()

            # Alert stats
            alert_stats = self.alert_service.get_alert_stats()

            # A/B testing stats
            ab_stats = self.ab_testing_service.get_summary_stats()

            # Log stats
            logger.info("=== SYSTEM HEALTH ===")
            logger.info(f"WebSocket Connections: {conn_stats['total_connections']}")
            logger.info(
                f"Active Alerts: {alert_stats['active_count']} (Critical: {alert_stats['active_by_severity']['critical']})"
            )
            logger.info(
                f"Prediction Logs: {ab_stats['total_predictions']} (Coverage: {ab_stats['coverage_percent']:.1f}%)"
            )
            logger.info(f"Active Experiments: {ab_stats['active_experiments']}")
            logger.info("====================")

            # Broadcast health status to connected clients
            health_data = {
                "type": "health_update",
                "timestamp": datetime.now().isoformat(),
                "data": {
                    "connections": conn_stats,
                    "alerts": alert_stats,
                    "predictions": ab_stats,
                },
            }

            await self.connection_manager.broadcast(health_data, group="dashboard")

        except Exception as e:
            logger.error(f"Error monitoring health: {e}", exc_info=True)

    async def send_keepalive_pings(self):
        """
        Send keepalive pings to all connections

        Runs every 30 seconds
        """
        try:
            await self.connection_manager.send_ping()
        except Exception as e:
            logger.error(f"Error sending pings: {e}", exc_info=True)

    def start(self):
        """Start all background tasks"""
        if self.is_running:
            logger.warning("Background tasks already running")
            return

        # Schedule tasks

        # Predictions every 5 minutes
        self.scheduler.add_job(
            self.broadcast_predictions,
            trigger=IntervalTrigger(minutes=5),
            id="broadcast_predictions",
            name="Broadcast Predictions",
            replace_existing=True,
        )

        # Alerts every 1 minute
        self.scheduler.add_job(
            self.check_alerts,
            trigger=IntervalTrigger(minutes=1),
            id="check_alerts",
            name="Check Alerts",
            replace_existing=True,
        )

        # Cleanup every hour
        self.scheduler.add_job(
            self.cleanup_old_data,
            trigger=IntervalTrigger(hours=1),
            id="cleanup_data",
            name="Cleanup Old Data",
            replace_existing=True,
        )

        # Health monitoring every 15 minutes
        self.scheduler.add_job(
            self.monitor_system_health,
            trigger=IntervalTrigger(minutes=15),
            id="monitor_health",
            name="Monitor System Health",
            replace_existing=True,
        )

        # Keepalive pings every 30 seconds
        self.scheduler.add_job(
            self.send_keepalive_pings,
            trigger=IntervalTrigger(seconds=30),
            id="keepalive_pings",
            name="Send Keepalive Pings",
            replace_existing=True,
        )

        # Start scheduler
        self.scheduler.start()
        self.is_running = True

        logger.info("✅ Background tasks started")
        logger.info("  - Predictions: every 5 minutes")
        logger.info("  - Alerts: every 1 minute")
        logger.info("  - Cleanup: every 1 hour")
        logger.info("  - Health monitoring: every 15 minutes")
        logger.info("  - Keepalive: every 30 seconds")

    def stop(self):
        """Stop all background tasks"""
        if not self.is_running:
            logger.warning("Background tasks not running")
            return

        self.scheduler.shutdown()
        self.is_running = False

        logger.info("Background tasks stopped")

    def get_task_status(self) -> dict:
        """Get status of all scheduled tasks"""
        if not self.is_running:
            return {"status": "stopped", "tasks": []}

        jobs = self.scheduler.get_jobs()

        tasks = []
        for job in jobs:
            next_run = job.next_run_time
            tasks.append(
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run": next_run.isoformat() if next_run else None,
                    "trigger": str(job.trigger),
                }
            )

        return {"status": "running", "tasks": tasks}


# Global service instance
_background_task_service = None


def get_background_task_service() -> BackgroundTaskService:
    """Get or create the global background task service instance"""
    global _background_task_service
    if _background_task_service is None:
        _background_task_service = BackgroundTaskService()
    return _background_task_service
