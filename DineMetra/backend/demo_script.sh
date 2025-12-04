#!/bin/bash
# DineMetra Demo Script - Fixed

echo "🎯 DINEMETRA LIVE DEMO"
echo "===================="
echo ""

echo "1️⃣  Wait Time Prediction (Party of 6, 85% occupancy):"
echo "---------------------------------------------------"
curl -s -X POST "http://localhost:8000/api/predictions/wait-time-enhanced" \
  -H "Content-Type: application/json" \
  -d '{"party_size": 6, "current_occupancy": 85}' | \
  python -c "import sys, json; d=json.load(sys.stdin); print(f'   Wait Time: {d[\"predicted_wait_minutes\"]} minutes'); print(f'   Confidence: {int(d[\"confidence\"]*100)}%'); print(f'   Category: {d[\"wait_category\"]}')"

echo ""
echo "2️⃣  Busyness Level:"
echo "-------------------"
curl -s -X POST "http://localhost:8000/api/predictions/busyness-enhanced" \
  -H "Content-Type: application/json" \
  -d '{}' | \
  python -c "import sys, json; d=json.load(sys.stdin); print(f'   Level: {d[\"level\"]}'); print(f'   Expected Guests: {d[\"expected_guests\"]}'); print(f'   Confidence: {int(d[\"confidence\"]*100)}%')"

echo ""
echo "3️⃣  Item Sales Forecast (The Pao - Best Seller):"
echo "-----------------------------------------------"
curl -s -X POST "http://localhost:8000/api/predictions/sales-enhanced" \
  -H "Content-Type: application/json" \
  -d '{"item_id": 1, "item_name": "The Pao", "category": "Rice Bowls"}' | \
  python -c "import sys, json; d=json.load(sys.stdin); print(f'   Predicted: {d[\"predicted_quantity\"]} units'); print(f'   Confidence: {int(d[\"confidence\"]*100)}%'); print(f'   Range: {d[\"margin\"][\"range\"]}'); print(f'   Recommendation: {d[\"recommendation\"]}')"

echo ""
echo "4️⃣  Live Events Detected:"
echo "------------------------"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); events=d['info_sections']['events'][:3]; print('\\n'.join([f'   • {e[\"event\"]} - {e[\"attendance\"]:,} people @ {e[\"distance\"]}' for e in events]))"

echo ""
echo "5️⃣  System Health:"
echo "------------------"
curl -s "http://localhost:8000/api/system/info" | \
  python -c "import sys, json; d=json.load(sys.stdin); print(f'   Active Connections: {d[\"info\"][\"websocket_connections\"][\"total_connections\"]}'); print(f'   Alert Rules: {d[\"info\"][\"alerts\"][\"rules_configured\"]}'); print(f'   Models Loaded: 3 (Wait Time, Busyness, Item Sales)')"

echo ""
echo "✅ Demo Complete!"
echo ""
echo "🌐 Resources:"
echo "   Dashboard: http://localhost:8000/api/dashboard/dashboard"
echo "   API Docs:  http://localhost:8000/docs"
echo "   WebSocket: ws://localhost:8000/ws/dashboard"