#!/bin/bash

echo "🧪 Testing CSV Upload Feature"
echo "=============================="
echo ""

# Check if February CSV exists
CSV_FILE="data/real/2025-02/02_Items.csv"

if [ ! -f "$CSV_FILE" ]; then
    echo "❌ February CSV not found at: $CSV_FILE"
    exit 1
fi

echo "📁 Found CSV: $CSV_FILE"
echo "📊 Uploading..."
echo ""

# Upload CSV
curl -X POST "http://localhost:8000/api/upload/upload-csv" \
  -F "file=@${CSV_FILE}" \
  -s | python -c "import sys, json; d=json.load(sys.stdin); print(f\"Status: {d['status']}\"); print(f\"Message: {d['message']}\")"

echo ""
echo "✅ Upload initiated!"
echo "💡 Connect to WebSocket to see real-time progress:"
echo "   ws://localhost:8000/ws/dashboard"
echo ""
echo "�� Check dashboard:"
echo "   http://localhost:8000/api/dashboard/dashboard"
