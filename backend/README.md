# Backend README

## Running the Backend

### Prerequisites
- Python 3.8+
- Tesseract OCR installed: https://github.com/UB-Mannheim/tesseract/wiki
- (Windows) Ensure Tesseract is installed at: `C:\Program Files\Tesseract-OCR\tesseract.exe`

### Installation

```bash
cd backend
pip install -r requirements.txt
```

### Running

```bash
cd backend
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Server will be available at: http://localhost:8000

### API Documentation

Once running, visit: http://localhost:8000/docs (interactive Swagger UI)

### API Endpoints

- `POST /identify_card` - Submit image and get card identification
- `GET /health` - Health check
- `GET /cards` - List available cards with pagination
- `POST /refresh_cache` - Force refresh card cache
