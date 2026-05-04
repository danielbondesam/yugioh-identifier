import React from 'react';

function Header({ backendHealth }) {
  return (
    <header className="bg-gradient-to-r from-purple-900 to-indigo-900 shadow-lg">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-white">
              🎴 Yu-Gi-Oh Identifier
            </h1>
            <p className="text-purple-200 text-sm mt-1">
              Identify cards using your camera
            </p>
          </div>
          
          <div className={`px-4 py-2 rounded-lg flex items-center gap-2 ${
            backendHealth 
              ? 'bg-green-500/20 text-green-300' 
              : 'bg-red-500/20 text-red-300'
          }`}>
            <div className={`w-2 h-2 rounded-full ${
              backendHealth ? 'bg-green-500' : 'bg-red-500'
            } ${backendHealth && 'animate-pulse'}`}></div>
            <span className="text-sm font-medium">
              {backendHealth ? 'Backend Online' : 'Backend Offline'}
            </span>
          </div>
        </div>
      </div>
    </header>
  );
}

export default Header;
