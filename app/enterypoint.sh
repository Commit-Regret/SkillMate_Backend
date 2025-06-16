#!/bin/bash

echo "📡 Waiting for Qdrant to be available at $QDRANT_HOST:$QDRANT_PORT..."

until curl -s "http://$QDRANT_HOST:$QDRANT_PORT/collections" > /dev/null; do
  echo "⏳ Still waiting for Qdrant..."
  sleep 2
done

echo "✅ Qdrant is available! Running populate.py..."
python populate.py || echo "⚠️ populate.py failed or already populated."

echo "🚀 Starting Flask-SocketIO app..."
exec python main.py
