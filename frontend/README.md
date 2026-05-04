# Frontend README

## Running the Frontend

### Prerequisites
- Node.js 16+ and npm

### Installation

```bash
cd frontend
npm install
```

### Development

```bash
cd frontend
npm start
```

The app will open at http://localhost:3000

### Build for Production

```bash
cd frontend
npm run build
```

## Configuration

The frontend connects to the backend at `http://localhost:8000` by default.

To change this, edit [src/App.js](src/App.js) and update the `fetch` URLs.
