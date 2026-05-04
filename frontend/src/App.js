import React, { useState, useEffect } from 'react';
import './index.css';
import CameraCapture from './components/CameraCapture';
import ResultDisplay from './components/ResultDisplay';
import Header from './components/Header';

function App() {
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [backendHealth, setBackendHealth] = useState(false);

  useEffect(() => {
    // Check backend health on mount
    checkBackendHealth();
    const interval = setInterval(checkBackendHealth, 30000); // Check every 30s
    return () => clearInterval(interval);
  }, []);

  const checkBackendHealth = async () => {
    try {
      const response = await fetch('http://localhost:8000/health');
      setBackendHealth(response.ok);
    } catch (err) {
      setBackendHealth(false);
      console.warn('Backend health check failed:', err.message);
    }
  };

  const handleCapture = async (blob) => {
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const formData = new FormData();
      formData.append('file', blob, 'capture.jpg');

      const response = await fetch('http://localhost:8000/identify_card', {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (!response.ok) {
        throw new Error(data.detail || 'Failed to identify card');
      }

      setResult(data);
    } catch (err) {
      setError(err.message || 'Error identifying card. Try again.');
      console.error('Error:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleRetry = () => {
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 to-slate-900">
      <Header backendHealth={backendHealth} />
      
      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {!result && !error && (
            <CameraCapture 
              onCapture={handleCapture} 
              loading={loading}
              backendReady={backendHealth}
            />
          )}

          {(result || error) && (
            <ResultDisplay 
              result={result}
              error={error}
              loading={loading}
              onRetry={handleRetry}
            />
          )}
        </div>
      </main>
    </div>
  );
}

export default App;
