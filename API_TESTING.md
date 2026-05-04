# API Testing Examples

Quick reference for testing the backend API.

## Using curl (command line)

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "cards_loaded": 11000
}
```

### List Cards
```bash
# Get first 10 cards
curl "http://localhost:8000/cards?limit=10&offset=0"

# Paginate through all cards
curl "http://localhost:8000/cards?limit=100&offset=100"
```

### Identify Card from Image
```bash
# Basic usage
curl -X POST http://localhost:8000/identify_card \
  -F "file=@path/to/card_image.jpg"

# Save response to file
curl -X POST http://localhost:8000/identify_card \
  -F "file=@card.jpg" > response.json

# Pretty print JSON response
curl -s -X POST http://localhost:8000/identify_card \
  -F "file=@card.jpg" | jq .
```

### Refresh Cache
```bash
curl -X POST http://localhost:8000/refresh_cache
```

## Using Python

### Using requests library

```python
import requests
import json

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Identify card
with open('card_image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/identify_card',
        files=files
    )
    result = response.json()
    print(json.dumps(result, indent=2))

# List cards
response = requests.get(
    'http://localhost:8000/cards',
    params={'limit': 10, 'offset': 0}
)
cards = response.json()
print(f"Total cards: {cards['total']}")
for card in cards['cards']:
    print(f"  - {card['name']}")

# Refresh cache
response = requests.post('http://localhost:8000/refresh_cache')
print(response.json())
```

## Using Swagger UI (Interactive)

1. Open http://localhost:8000/docs
2. Browse endpoints
3. Click "Try it out" on any endpoint
4. Fill in parameters
5. Click "Execute"

## Response Examples

### Successful Match

```json
{
  "success": true,
  "name": "Blue-Eyes White Dragon",
  "type": "Synchro/Effect Monster",
  "confidence": 0.95,
  "ocr_confidence": 0.92,
  "match_score": 98,
  "atk": 3000,
  "def": 2500,
  "level": 8,
  "attribute": "LIGHT",
  "race": "Dragon",
  "description": "2 Tuner monsters...",
  "image_url": "https://...",
  "extracted_name": "BLUE EYES WHITE DRAGON"
}
```

### Partial Match (Candidates)

```json
{
  "success": false,
  "message": "No exact match found, showing top candidates",
  "extracted_name": "BLUE EYES",
  "ocr_confidence": 0.85,
  "candidates": [
    {
      "name": "Blue-Eyes White Dragon",
      "type": "Synchro/Effect Monster",
      "description": "2 Tuner monsters...",
      "image_url": "https://...",
      "confidence": 0.92,
      "match_score": 92
    },
    {
      "name": "Blue-Eyes Alternative White Dragon",
      "type": "Synchro/Effect Monster",
      "description": "...",
      "image_url": "https://...",
      "confidence": 0.85,
      "match_score": 85
    }
  ]
}
```

### Error Response

```json
{
  "detail": "Card not found: INVALID CARD NAME"
}
```

## Batch Testing

### Test Multiple Images

```bash
#!/bin/bash

for image in test_images/*.jpg; do
    echo "Testing: $image"
    curl -X POST http://localhost:8000/identify_card \
      -F "file=@$image" | jq '.name, .confidence'
    echo "---"
done
```

### Load Testing

```bash
# Using Apache Bench (ab)
ab -n 100 -c 10 -p test_image.jpg \
  http://localhost:8000/identify_card

# Using wrk
wrk -t4 -c100 -d30s \
  -s post_script.lua \
  http://localhost:8000/identify_card
```

## Debugging

### Enable Verbose Output

```bash
# Print headers
curl -v -X POST http://localhost:8000/identify_card \
  -F "file=@card.jpg"

# Show timing
curl -w "Time: %{time_total}s\n" \
  http://localhost:8000/health

# Follow redirects
curl -L http://localhost:8000/health
```

### Check Server Logs

```bash
# Backend terminal will show:
# - Request received
# - Processing steps
# - Errors and warnings
# - Response sent
```

## Common Issues & Solutions

### Connection Refused
- Backend not running on port 8000
- Start backend: `python -m uvicorn app.main:app --port 8000`

### 422 Unprocessable Entity
- Missing or invalid image file
- Check file format is JPEG/PNG
- File must be in binary mode

### 500 Internal Server Error
- Card database not loaded
- Check backend logs
- Restart backend: kill and restart process

### Slow Responses (>1 second)
- Normal on first request (loading database)
- Tesseract taking time (200-300ms is normal)
- Check CPU usage during identification

## Tips

1. **Test with Swagger UI first** - Easier than curl
2. **Capture API responses** - Save to JSON for analysis
3. **Monitor backend logs** - See what's happening
4. **Use jq for parsing** - Pretty print JSON responses
5. **Measure timing** - Use curl -w to track performance
