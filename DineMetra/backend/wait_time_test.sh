# Test wait time with different scenarios
echo "=== Test 1: Wait Time - Busy Friday Night ==="
curl -X POST "http://localhost:8000/api/predictions/wait-time-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "party_size": 6,
    "current_occupancy": 85,
    "timestamp": "2025-12-06T19:00:00"
  }' | python -m json.tool

echo ""
echo "=== Test 2: Wait Time - Quiet Tuesday Afternoon ==="
curl -X POST "http://localhost:8000/api/predictions/wait-time-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "party_size": 2,
    "current_occupancy": 30,
    "timestamp": "2025-12-03T14:00:00"
  }' | python -m json.tool