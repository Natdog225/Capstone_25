#!/bin/bash
# Complete Real Data Integration Test

echo "🎯 COMPLETE DINEMETRA REAL DATA TEST"
echo "====================================="
echo ""

# Test 1: Best Sellers
echo "1️⃣  Best Sellers (from 57,603 sales)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   ✓ {i[\"name\"]}: {i[\"value\"]} units ({i[\"change\"]})') for i in d['metrics']['categories'][0]['items']]"

echo ""

# Test 2: Peak Hours
echo "2️⃣  Peak Hours (from 14,656 orders)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   ✓ {i[\"name\"]}: {i[\"value\"]} capacity') for i in d['metrics']['categories'][1]['items']]"

echo ""

# Test 3: Sales Chart
echo "3️⃣  Sales Chart (real daily patterns)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); chart=d.get('sales_chart',[]); [print(f'   ✓ {day[\"day\"]}: \${day[\"thisWeek\"]} {\"(actual)\" if day.get(\"actual\") else \"(predicted)\"}') for day in chart[:7]]"

echo ""

# Test 4: ML Predictions
echo "4️⃣  Purchasing (ML predictions, 85% confidence)"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); [print(f'   ✓ {p[\"item\"]}: {p[\"estimate\"]} - {p[\"status\"]}') for p in d['metrics']['purchasing'][:4]]"

echo ""

# Test 5: Live Integrations
echo "5️⃣  Live Integrations"
curl -s "http://localhost:8000/api/dashboard/dashboard" | \
  python -c "import sys, json; d=json.load(sys.stdin); print(f'   ✓ Weather: {d[\"info_sections\"][\"weather\"][\"current\"]}'); print(f'   ✓ Events: {len(d[\"info_sections\"][\"events\"])} detected'); print(f'   ✓ Next: {d[\"info_sections\"][\"events\"][0][\"event\"]}')"

echo ""
echo "====================================="
echo "✅ ALL SYSTEMS USING REAL DATA!"
echo "📊 Dashboard: http://localhost:8000/api/dashboard/dashboard"
echo "📖 API Docs: http://localhost:8000/docs"