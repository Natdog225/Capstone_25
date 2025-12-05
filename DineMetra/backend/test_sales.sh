#!/bin/bash
# Test Real Data Integration - FIXED

echo "🧪 TESTING REAL DATA INTEGRATION"
echo "================================"
echo ""

echo "1️⃣  Best Sellers (should show Soda, The Pao, etc.)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   • {i[\"name\"]}: {i[\"value\"]} units') for i in d['metrics']['categories'][0]['items']]"

echo ""
echo "2️⃣  Peak Hours (should show actual hours from orders)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   • {i[\"name\"]}: {i[\"value\"]}') for i in d['metrics']['categories'][1]['items']]"

echo ""
echo "3️⃣  Sales Chart (should reflect real daily patterns)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); chart=d.get('sales_chart', []); [print(f'   • {day[\"day\"]}: \${day[\"thisWeek\"]}') for day in chart[:3]] if chart else print('   No chart data')"

echo ""
echo "4️⃣  Purchasing (should use real predictions)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   • {p[\"item\"]}: {p[\"estimate\"]} ({p[\"quantity\"]} units)') for p in d['metrics']['purchasing'][:4]]"

echo ""
echo "================================"
echo "✅ Test Complete!"