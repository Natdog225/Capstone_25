"""
WebSocket Connection Test
Tests real-time WebSocket connection to DineMetra API
"""

import asyncio
import websockets
import json


async def test_dashboard():
    uri = "ws://localhost:8000/ws/dashboard?client_id=test_user"

    print("=" * 60)
    print("WEBSOCKET CONNECTION TEST")
    print("=" * 60)
    print(f"\nConnecting to: {uri}\n")

    try:
        async with websockets.connect(uri) as websocket:
            print("✓ Connected to dashboard WebSocket\n")

            # 1. Receive welcome message
            message = await websocket.recv()
            data = json.loads(message)
            print(f"1. Welcome Message:")
            print(f"   Type: {data['type']}")
            print(f"   Status: {data['status']}")
            print(f"   Connection ID: {data['connection_id']}\n")

            # 2. Send ping
            await websocket.send(json.dumps({"type": "ping"}))
            print(f"2. Sent: ping\n")

            # 3. Receive pong
            message = await websocket.recv()
            data = json.loads(message)
            print(f"3. Received Pong:")
            print(f"   Type: {data['type']}")
            print(f"   Timestamp: {data['timestamp']}\n")

            print("=" * 60)
            print("✅ WebSocket test PASSED!")
            print("=" * 60)

    except websockets.exceptions.WebSocketException as e:
        print("=" * 60)
        print("WebSocket test FAILED!")
        print("=" * 60)
        print(f"\nError: {e}\n")
        print("Troubleshooting:")
        print("1. Check server is running: curl http://localhost:8000/docs")
        print("2. Verify websocket router is included in main.py")
        print("3. Check logs for errors")

    except Exception as e:
        print("=" * 60)
        print("Unexpected error!")
        print("=" * 60)
        print(f"\nError: {e}\n")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(test_dashboard())
