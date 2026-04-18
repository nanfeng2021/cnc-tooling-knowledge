#!/bin/bash
# Start the Tooling RAG API server
# Usage: ./start_server.sh [port]

PORT=${1:-8000}

cd "$(dirname "$0")"

echo "=================================================="
echo "  Tooling RAG Knowledge Base API Server"
echo "=================================================="
echo ""

if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: pip install -r requirements.txt"
    exit 1
fi

source venv/bin/activate

echo "🚀 Starting server on port $PORT..."
echo ""
echo "📚 API Documentation:"
echo "   Swagger UI:  http://localhost:$PORT/docs"
echo "   ReDoc:       http://localhost:$PORT/redoc"
echo ""
echo "📝 Example Requests:"
echo "   Health Check:"
echo "   curl http://localhost:$PORT/health"
echo ""
echo "   Search Cutters:"
echo "   curl -X POST http://localhost:$PORT/search \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"query\": \"carbide end mill for steel\", \"top_k\": 3}'"
echo ""
echo "=================================================="
echo ""

python -m uvicorn src.interface.api.api:app --reload --host 0.0.0.0 --port "$PORT"
