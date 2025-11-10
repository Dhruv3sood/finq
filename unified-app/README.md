# FinLore - Unified Financial Analysis & Presentation Application

A unified application that combines Balance Sheet RAG (Retrieval-Augmented Generation) and PPT Generator functionalities into a single interface.

## Features

### RAG Chat
- Upload balance sheet files (CSV, TXT)
- Get AI-powered summaries of financial data
- Chat with your balance sheet data using RAG technology
- Ask questions about financial metrics and trends

### PPT Generator
- Upload balance sheet and company profile files
- Generate professional PowerPoint presentations
- Multiple template styles (Professional, Modern, Financial, Executive)
- Customizable themes and slide selection
- Preview and download PowerPoint files

## Architecture

- **Frontend**: React + Vite + TailwindCSS (Port 3000)
- **RAG Backend**: Flask (Port 5002)
- **PPT Backend**: Flask (Port 5001)

## Setup

### Prerequisites
- Node.js 18+
- Python 3.8+
- OpenAI API Key

### Backend Setup

1. **RAG Backend** (Balance Sheet RAG):
   ```bash
   cd ../balance-sheet-rag/backend
   pip install -r requirements.txt
   python app.py
   ```
   Runs on http://localhost:5002

2. **PPT Backend** (PPT Generator):
   ```bash
   cd ../ppt-generator/backend
   pip install -r requirements.txt
   # Create .env file with OPENAI_API_KEY
   echo "OPENAI_API_KEY=your_key_here" > .env
   python app.py
   ```
   Runs on http://localhost:5001

### Frontend Setup

```bash
cd unified-app/frontend
npm install
npm run dev
```

Runs on http://localhost:3000

## Usage

1. Start both backends (RAG on 5002, PPT on 5001)
2. Start the unified frontend (port 3000)
3. Access http://localhost:3000
4. Use the tabs to switch between:
   - **RAG Chat**: Upload balance sheet and chat with your data
   - **PPT Generator**: Upload files and generate presentations

## API Endpoints

### RAG Backend (5002)
- `POST /api/upload` - Upload balance sheet file
- `POST /api/chat` - Chat with balance sheet data
- `GET /api/health` - Health check

### PPT Backend (5001)
- `POST /api/upload` - Upload balance sheet and company profile
- `POST /api/generate` - Generate presentation
- `GET /api/download/<session_id>` - Download presentation
- `GET /api/preview/<session_id>` - Preview slides
- `GET /api/health` - Health check

## Project Structure

```
unified-app/
  frontend/
    src/
      components/
        rag/          # RAG Chat components
        ppt/          # PPT Generator components
      services/
        api.js        # Unified API service
      App.jsx         # Main app with tabs
      main.jsx
```

