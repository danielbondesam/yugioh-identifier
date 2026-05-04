import React, { useRef, useState, useEffect } from 'react';

function CameraCapture({ onCapture, loading, backendReady }) {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [cameraError, setCameraError] = useState(null);

  useEffect(() => {
    if (!cameraActive) return;

    const startCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            facingMode: 'environment',
            width: { ideal: 1280 },
            height: { ideal: 720 },
          },
        });

        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          // Força o vídeo a reproduzir (necessário em mobile)
          videoRef.current.play().catch(err => {
            console.warn('Autoplay failed:', err);
          });
          setCameraError(null);
        }
      } catch (err) {
        let errorMessage = 'Camera access denied. Please allow camera permissions.';
        
        if (err.name === 'NotAllowedError') {
          errorMessage = 'Camera permission denied. Please grant camera access in settings.';
        } else if (err.name === 'NotFoundError') {
          errorMessage = 'No camera device found on this device.';
        } else if (err.name === 'NotSecureError') {
          errorMessage = 'HTTPS or localhost is required for camera access.';
        }
        
        setCameraError(errorMessage);
        console.error('Camera error:', err.name, err.message);
      }
    };

    startCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
        videoRef.current.srcObject = null;
      }
    };
  }, [cameraActive]);

  const handleCapture = () => {
    if (!videoRef.current || !canvasRef.current) return;

    const context = canvasRef.current.getContext('2d');
    canvasRef.current.width = videoRef.current.videoWidth;
    canvasRef.current.height = videoRef.current.videoHeight;

    context.drawImage(
      videoRef.current,
      0,
      0,
      canvasRef.current.width,
      canvasRef.current.height
    );

    canvasRef.current.toBlob(
      (blob) => {
        onCapture(blob);
        setCameraActive(false);
      },
      'image/jpeg',
      0.95
    );
  };

  if (!cameraActive) {
    return (
      <div className="space-y-6">
        <div className="bg-gradient-to-br from-slate-800 to-slate-700 rounded-xl p-8 text-center">
          <div className="text-6xl mb-4">📷</div>
          <h2 className="text-2xl font-bold text-white mb-2">Ready to Scan?</h2>
          <p className="text-slate-300 mb-6">
            Position your Yu-Gi-Oh card in the center of your screen with good lighting
          </p>

          {cameraError && (
            <div className="bg-red-500/10 border border-red-500/30 text-red-300 px-4 py-3 rounded-lg mb-6">
              {cameraError}
            </div>
          )}

          {!backendReady && (
            <div className="bg-yellow-500/10 border border-yellow-500/30 text-yellow-300 px-4 py-3 rounded-lg mb-6">
              ⚠️ Backend not ready. Make sure the server is running on port 8000.
            </div>
          )}

          <button
            onClick={() => setCameraActive(true)}
            disabled={loading || !backendReady}
            className={`px-8 py-3 rounded-lg font-semibold text-white transition-all ${
              loading || !backendReady
                ? 'bg-slate-600 cursor-not-allowed opacity-50'
                : 'bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 active:scale-95'
            }`}
          >
            {loading ? 'Processing...' : 'Open Camera'}
          </button>
        </div>

        <div className="bg-slate-800 rounded-xl p-6">
          <h3 className="text-white font-semibold mb-3">📋 How to Use:</h3>
          <ol className="space-y-2 text-slate-300 text-sm">
            <li>1. Tap "Open Camera" to start</li>
            <li>2. Place your card in the center with good lighting</li>
            <li>3. Tap "Capture" when ready</li>
            <li>4. View your card details below</li>
          </ol>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <div className="relative bg-black rounded-xl overflow-hidden aspect-video">
        <video
          ref={videoRef}
          autoPlay
          playsInline
          className="w-full h-full object-cover"
        />

        {/* ROI Overlay */}
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="relative">
            {/* Card frame guide */}
            <div
              className="border-2 border-dashed border-green-400 pointer-events-none"
              style={{
                width: '400px',
                height: '600px',
                boxShadow: '0 0 0 9999px rgba(0, 0, 0, 0.5)',
              }}
            >
              <div className="absolute -top-8 left-0 text-green-400 text-xs font-mono">
                Place card here
              </div>
            </div>
          </div>
        </div>

        {/* Scanning indicator */}
        {loading && (
          <div className="absolute inset-0 bg-black/40 flex items-center justify-center">
            <div className="flex flex-col items-center gap-2">
              <div className="w-12 h-12 border-4 border-purple-500/30 border-t-purple-500 rounded-full animate-spin"></div>
              <p className="text-white text-sm">Identifying card...</p>
            </div>
          </div>
        )}
      </div>

      <div className="flex gap-3">
        <button
          onClick={() => setCameraActive(false)}
          className="flex-1 px-4 py-2 rounded-lg bg-slate-700 hover:bg-slate-600 text-white font-semibold transition-colors"
        >
          Cancel
        </button>

        <button
          onClick={handleCapture}
          disabled={loading}
          className={`flex-1 px-4 py-2 rounded-lg font-semibold text-white transition-all ${
            loading
              ? 'bg-slate-600 cursor-not-allowed opacity-50'
              : 'bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-500 hover:to-emerald-500 active:scale-95'
          }`}
        >
          {loading ? 'Processing...' : '📸 Capture'}
        </button>
      </div>

      <canvas ref={canvasRef} className="hidden" />
    </div>
  );
}

export default CameraCapture;
