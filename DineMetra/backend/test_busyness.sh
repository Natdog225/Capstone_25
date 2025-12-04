echo "=== Test 3: Busyness - Lunch Rush ==="
curl -X POST "http://localhost:8000/api/predictions/busyness-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-12-03T12:00:00"
  }' | python -m json.tool

echo ""
echo "=== Test 4: Busyness - Late Night ==="
curl -X POST "http://localhost:8000/api/predictions/busyness-enhanced" \
  -H "Content-Type: application/json" \
  -d '{
    "timestamp": "2025-12-03T22:00:00"
  }' | python -m json.tool