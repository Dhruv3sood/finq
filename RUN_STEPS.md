# How to Run FinLore Unified Application

## Prerequisites
- Python 3.8+
- Node.js 18+
- OpenAI API Key

## Step-by-Step Instructions

### Step 1: Kill Old Processes (if any)
```bash
# Kill processes on ports 5000, 5001, 5002, 3000
lsof -ti:5000,5001,5002,3000 | xargs kill -9 2>/dev/null || true
```

### Step 2: Setup Backend

1. Navigate to backend directory:
```bash
cd app/backend
```

2. Install Python dependencies:
```bash
pip install -r requirements.txt
```

3. Create `.env` file with your OpenAI API key:
```bash
echo "OPENAI_API_KEY=your_api_key_here" > .env
```

**Important:** Replace `your_api_key_here` with your actual OpenAI API key. Never commit API keys to version control!

4. Start the backend server:
```bash
python app.py
```

The backend will run on **http://localhost:5000**

### Step 3: Setup Frontend (in a new terminal)

1. Navigate to frontend directory:
```bash
cd app/frontend
```

2. Install Node dependencies (if not already installed):
```bash
npm install
```

3. Start the frontend development server:
```bash
npm run dev
```

The frontend will run on **http://localhost:3000**

### Step 4: Access the Application

Open your browser and go to:
```
http://localhost:3000
```

## Quick Start Script

Alternatively, you can use the start script:

```bash
cd app
chmod +x start.sh
./start.sh
```

Note: Make sure to start the backend first before running the start script.

## Verify Services are Running

Check if services are running:
```bash
# Check backend
curl http://localhost:5000/api/health

# Check frontend (should show Vite dev server)
curl http://localhost:3000
```

## Application Features

### RAG Chat Tab
- Upload balance sheet (required) and company profile (optional)
- Chat with your financial data using AI
- Get insights about your balance sheet entries

### PPT Generator Tab
- Upload balance sheet and company profile
- Configure template and theme
- Generate and preview PowerPoint presentation
- Download the generated presentation

## Troubleshooting

### Backend not starting
- Check if port 5000 is available: `lsof -i :5000`
- Verify `.env` file exists and has valid API key
- Check Python dependencies: `pip install -r requirements.txt`

### Frontend not starting
- Check if port 3000 is available: `lsof -i :3000`
- Verify Node dependencies: `npm install`
- Check for proxy configuration in `vite.config.js`

### API Connection Issues
- Ensure backend is running on port 5000
- Check `vite.config.js` has correct proxy configuration
- Verify CORS is enabled in backend

## Stopping the Application

To stop all services:
```bash
# Kill backend
lsof -ti:5000 | xargs kill -9

# Kill frontend
lsof -ti:3000 | xargs kill -9
```

