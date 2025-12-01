"""
WebSocket API Endpoints
Real-time communication endpoints for live updates
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from datetime import datetime
import asyncio
import logging
import uuid

from app.websocket.manager import get_connection_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ws", tags=["websocket"])


@router.websocket("/dashboard")
async def websocket_dashboard(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket endpoint for real-time dashboard updates

    Receives:
    - Live prediction updates every 5 minutes
    - Event notifications
    - Weather updates

    Usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/dashboard?client_id=user123');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'prediction_update') {
            updateDashboard(data.data);
        }
    };
    ```
    """
    manager = get_connection_manager()

    # Generate connection ID
    connection_id = client_id or f"dashboard_{uuid.uuid4().hex[:8]}"

    # Connect
    connected = await manager.connect(websocket, connection_id, group="dashboard")

    if not connected:
        return

    try:
        # Keep connection alive and handle incoming messages
        while True:
            # Receive message from client
            data = await websocket.receive_json()

            # Handle different message types
            message_type = data.get("type")

            if message_type == "ping":
                # Respond to ping
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    connection_id,
                )

            elif message_type == "subscribe":
                # Client subscribing to specific updates
                logger.info(
                    f"Client {connection_id} subscribed to: {data.get('channels')}"
                )
                await manager.send_personal_message(
                    {
                        "type": "subscribed",
                        "channels": data.get("channels", []),
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )

            elif message_type == "request_update":
                # Client requesting immediate update
                logger.info(f"Client {connection_id} requested update")
                # Trigger update (handled by background task)
                await manager.send_personal_message(
                    {
                        "type": "update_scheduled",
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )

    except WebSocketDisconnect:
        logger.info(f"Client {connection_id} disconnected normally")
        manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        manager.disconnect(connection_id)


@router.websocket("/alerts")
async def websocket_alerts(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket endpoint for real-time alerts

    Receives:
    - Critical alerts (wait time > 45 min)
    - Warning alerts (occupancy > 90%)
    - Info alerts (nearby events)

    Usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/alerts?client_id=manager1');

    ws.onmessage = (event) => {
        const alert = JSON.parse(event.data);
        if (alert.type === 'alert') {
            showNotification(alert.data);
        }
    };
    ```
    """
    manager = get_connection_manager()

    # Generate connection ID
    connection_id = client_id or f"alerts_{uuid.uuid4().hex[:8]}"

    # Connect
    connected = await manager.connect(websocket, connection_id, group="alerts")

    if not connected:
        return

    try:
        while True:
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    connection_id,
                )

            elif message_type == "acknowledge":
                # Client acknowledged an alert
                alert_id = data.get("alert_id")
                logger.info(f"Client {connection_id} acknowledged alert: {alert_id}")
                await manager.send_personal_message(
                    {
                        "type": "alert_acknowledged",
                        "alert_id": alert_id,
                        "timestamp": datetime.now().isoformat(),
                    },
                    connection_id,
                )

    except WebSocketDisconnect:
        logger.info(f"Alert client {connection_id} disconnected normally")
        manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        manager.disconnect(connection_id)


@router.websocket("/predictions")
async def websocket_predictions(websocket: WebSocket, client_id: str = Query(None)):
    """
    WebSocket endpoint for streaming prediction updates

    Receives:
    - Real-time prediction updates as they're calculated
    - Model performance metrics
    - A/B test results

    Usage:
    ```javascript
    const ws = new WebSocket('ws://localhost:8000/ws/predictions?client_id=admin1');

    ws.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'prediction_update') {
            console.log('New prediction:', data.data);
        }
    };
    ```
    """
    manager = get_connection_manager()

    # Generate connection ID
    connection_id = client_id or f"predictions_{uuid.uuid4().hex[:8]}"

    # Connect
    connected = await manager.connect(websocket, connection_id, group="predictions")

    if not connected:
        return

    try:
        while True:
            data = await websocket.receive_json()

            message_type = data.get("type")

            if message_type == "ping":
                await manager.send_personal_message(
                    {"type": "pong", "timestamp": datetime.now().isoformat()},
                    connection_id,
                )

    except WebSocketDisconnect:
        logger.info(f"Predictions client {connection_id} disconnected normally")
        manager.disconnect(connection_id)

    except Exception as e:
        logger.error(f"WebSocket error for {connection_id}: {e}")
        manager.disconnect(connection_id)
