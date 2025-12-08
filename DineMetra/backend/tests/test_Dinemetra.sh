#!/bin/bash
# Complete DineMetra Test Suite

echo "🧪 DINEMETRA COMPLETE TEST SUITE"
echo "================================"
echo ""

BASE_URL="http://localhost:8000"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

test_endpoint() {
  local name=$1
  local url=$2
  local method=${3:-GET}
  local data=$4
  
  echo -n "Testing $name... "
  
  if [ "$method" = "POST" ]; then
    response=$(curl -s -X POST "$BASE_URL$url" \
      -H "Content-Type: application/json" \
      -d "$data")
  else
    response=$(curl -s "$BASE_URL$url")
  fi
  
  if echo "$response" | grep -q "error"; then
    echo -e "${RED}FAIL${NC}"
    return 1
  else
    echo -e "${GREEN}PASS${NC}"
    return 0
  fi
}

# Run tests
echo "1. System Health"
test_endpoint "System Info" "/api/system/info"
echo ""

echo "2. Core Predictions"
test_endpoint "Wait Time" "/api/predictions/wait-time-enhanced" "POST" '{"party_size":4,"current_occupancy":75}'
test_endpoint "Busyness" "/api/predictions/busyness-enhanced" "POST" '{}'
test_endpoint "Item Sales" "/api/predictions/sales-enhanced" "POST" '{"item_id":1,"item_name":"The Pao","category":"Rice Bowls"}'
echo ""

echo "3. Dashboard"
test_endpoint "Dashboard" "/api/dashboard/dashboard"
echo ""

echo "4. Integration"
test_endpoint "Historical" "/api/historical/compare/all?date=2025-12-03"
echo ""

echo "================================"
echo "✅ Test suite complete!"