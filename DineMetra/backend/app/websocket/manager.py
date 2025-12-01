"""
WebSocket Connection Manager
Handles real-time connections for live updates and notifications
"""

from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List, Set
import json
import asyncio
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections for real-time updates

    Features:
    - Connection pooling
    - Broadcast to all clients
    - Targeted messaging
    - Automatic cleanup
    """

    def __init__(self):
        # Active connections by connection_id
        self.active_connections: Dict[str, WebSocket] = {}

        # Group connections by type (dashboard, alerts, etc.)
        self.connection_groups: Dict[str, Set[str]] = {
            "dashboard": set(),
            "alerts": set(),
            "predictions": set(),
        }

        # Connection metadata
        self.connection_info: Dict[str, dict] = {}

        logger.info("WebSocket ConnectionManager initialized")

    async def connect(
        self, websocket: WebSocket, connection_id: str, group: str = "dashboard"
    ) -> bool:
        """
        Accept and register a new WebSocket connection

        Args:
            websocket: WebSocket connection
            connection_id: Unique identifier for this connection
            group: Connection group (dashboard, alerts, predictions)

        Returns:
            bool: True if connected successfully
        """
        try:
            await websocket.accept()

            self.active_connections[connection_id] = websocket
            self.connection_groups[group].add(connection_id)
            self.connection_info[connection_id] = {
                "group": group,
                "connected_at": datetime.now().isoformat(),
                "message_count": 0,
            }

            logger.info(f"✓ WebSocket connected: {connection_id} (group: {group})")
            logger.info(f"  Total connections: {len(self.active_connections)}")

            # Send welcome message
            await self.send_personal_message(
                {
                    "type": "connection",
                    "status": "connected",
                    "connection_id": connection_id,
                    "timestamp": datetime.now().isoformat(),
                },
                connection_id,
            )

            return True

        except Exception as e:
            logger.error(f"Error connecting WebSocket {connection_id}: {e}")
            return False

    def disconnect(self, connection_id: str):
        """
        Remove a WebSocket connection

        Args:
            connection_id: Connection to remove
        """
        if connection_id in self.active_connections:
            # Remove from active connections
            del self.active_connections[connection_id]

            # Remove from all groups
            for group in self.connection_groups.values():
                group.discard(connection_id)

            # Remove metadata
            if connection_id in self.connection_info:
                del self.connection_info[connection_id]

            logger.info(f"✓ WebSocket disconnected: {connection_id}")
            logger.info(f"  Remaining connections: {len(self.active_connections)}")

    async def send_personal_message(self, message: dict, connection_id: str):
        """
        Send message to a specific connection

        Args:
            message: Message to send
            connection_id: Target connection
        """
        if connection_id in self.active_connections:
            try:
                websocket = self.active_connections[connection_id]
                await websocket.send_json(message)

                # Update message count
                if connection_id in self.connection_info:
                    self.connection_info[connection_id]["message_count"] += 1

            except Exception as e:
                logger.error(f"Error sending to {connection_id}: {e}")
                self.disconnect(connection_id)

    async def broadcast(self, message: dict, group: str = None):
        """
        Broadcast message to all connections or specific group

        Args:
            message: Message to broadcast
            group: Optional group to target (dashboard, alerts, predictions)
        """
        # Add timestamp if not present
        if "timestamp" not in message:
            message["timestamp"] = datetime.now().isoformat()

        # Determine target connections
        if group and group in self.connection_groups:
            target_ids = self.connection_groups[group]
        else:
            target_ids = set(self.active_connections.keys())

        logger.info(
            f"📡 Broadcasting to {len(target_ids)} connections (group: {group or 'all'})"
        )

        # Send to all target connections
        disconnected = []
        for connection_id in target_ids:
            if connection_id in self.active_connections:
                try:
                    websocket = self.active_connections[connection_id]
                    await websocket.send_json(message)

                    # Update message count
                    if connection_id in self.connection_info:
                        self.connection_info[connection_id]["message_count"] += 1

                except Exception as e:
                    logger.error(f"Error broadcasting to {connection_id}: {e}")
                    disconnected.append(connection_id)

        # Clean up disconnected
        for connection_id in disconnected:
            self.disconnect(connection_id)

    async def broadcast_prediction_update(self, prediction_data: dict):
        """
        Broadcast prediction update to all dashboard connections

        Args:
            prediction_data: Prediction data to broadcast
        """
        message = {
            "type": "prediction_update",
            "data": prediction_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message, group="dashboard")

    async def broadcast_alert(self, alert_data: dict):
        """
        Broadcast alert to all alert connections

        Args:
            alert_data: Alert data to broadcast
        """
        message = {
            "type": "alert",
            "data": alert_data,
            "timestamp": datetime.now().isoformat(),
        }
        await self.broadcast(message, group="alerts")

    def get_connection_stats(self) -> dict:
        """
        Get connection statistics

        Returns:
            dict: Connection statistics
        """
        stats = {
            "total_connections": len(self.active_connections),
            "groups": {
                group: len(connections)
                for group, connections in self.connection_groups.items()
            },
            "connections": [],
        }

        for connection_id, info in self.connection_info.items():
            stats["connections"].append({"id": connection_id, **info})

        return stats

    async def send_ping(self):
        """
        Send ping to all connections to keep them alive
        """
        message = {"type": "ping", "timestamp": datetime.now().isoformat()}
        await self.broadcast(message)


# Global connection manager instance
manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance"""
    return manager
