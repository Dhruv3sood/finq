#!/bin/bash

# Start script for FinLore Unified Application

echo "Starting FinLore Unified Application..."
echo ""

# Check if backend is running
check_backend() {
    port=$1
    name=$2
    if curl -s http://localhost:$port/api/health > /dev/null 2>&1; then
        echo "✓ $name backend is running on port $port"
        return 0
    else
        echo "✗ $name backend is not running on port $port"
        return 1
    fi
}

# Check unified backend
BACKEND_RUNNING=false

if check_backend 5000 "Unified"; then
    BACKEND_RUNNING=true
fi

echo ""
if [ "$BACKEND_RUNNING" = false ]; then
    echo "Please start the backend first:"
    echo ""
    echo "  Unified Backend: cd unified-app/backend && python app.py"
    echo ""
    read -p "Press Enter to continue starting frontend anyway..."
fi

# Start frontend
echo "Starting frontend..."
cd frontend
npm run dev
