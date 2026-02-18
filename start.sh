#!/bin/bash
# Start the trading platform backend and frontend

echo "🚀 Starting Quantitative Trading Platform..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install Python dependencies if needed
if [ ! -f "venv/installed" ]; then
    echo "Installing Python dependencies..."
    pip install -r requirements.txt
    touch venv/installed
fi

# Initialize database
echo "Initializing database..."
python -c "from backend.core.db_utils import init_db; init_db()" 2>/dev/null || echo "Database already initialized"

# Start backend server
echo "Starting backend API server on http://localhost:8000..."
python -m uvicorn backend.api.main:app --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
sleep 3

# Start frontend (if Node.js is available)
if command -v npm &> /dev/null; then
    echo "Starting frontend development server on http://localhost:3000..."
    cd frontend
    
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    cd ..
else
    echo "⚠️  npm not found. Skipping frontend. Install Node.js to run the web interface."
fi

echo ""
echo "✅ Platform is running!"
echo ""
echo "📊 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
if command -v npm &> /dev/null; then
    echo "🖥️  Frontend: http://localhost:3000"
fi
echo ""
echo "Press Ctrl+C to stop all services..."

# Wait for user interrupt
trap "echo 'Stopping services...'; kill $BACKEND_PID 2>/dev/null; kill $FRONTEND_PID 2>/dev/null; exit" INT
wait
