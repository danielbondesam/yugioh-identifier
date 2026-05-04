import React from 'react';

function ResultDisplay({ result, error, loading, onRetry }) {
  if (error) {
    return (
      <div className="space-y-4 animate-slideIn">
        <div className="bg-red-500/10 border border-red-500/30 rounded-xl p-6">
          <div className="flex items-start gap-4">
            <div className="text-4xl">❌</div>
            <div className="flex-1">
              <h3 className="text-white font-semibold text-lg mb-1">
                Identification Failed
              </h3>
              <p className="text-red-200 text-sm mb-4">{error}</p>
              <button
                onClick={onRetry}
                className="px-4 py-2 rounded-lg bg-red-600 hover:bg-red-500 text-white font-semibold transition-colors"
              >
                Try Again
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (!result) return null;

  // Handle "no exact match" case with candidates
  if (!result.success && result.candidates) {
    return (
      <div className="space-y-6 animate-slideIn">
        <div className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-6">
          <h3 className="text-white font-semibold mb-2">No Exact Match Found</h3>
          <p className="text-yellow-200 text-sm mb-4">
            Extracted: <strong>{result.extracted_name}</strong>
          </p>
          <p className="text-yellow-200 text-sm">
            Here are the closest matches:
          </p>
        </div>

        <div className="grid gap-4">
          {result.candidates.map((card, idx) => (
            <CardCandidate key={idx} card={card} rank={idx + 1} />
          ))}
        </div>

        <button
          onClick={onRetry}
          className="w-full px-4 py-2 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold transition-all active:scale-95"
        >
          Try Again
        </button>
      </div>
    );
  }

  // Handle successful match
  if (result.success) {
    return (
      <div className="space-y-6 animate-slideIn">
        <div className="bg-gradient-to-br from-green-900/30 to-emerald-900/30 border border-green-500/30 rounded-xl p-6">
          <div className="flex items-start justify-between mb-4">
            <div>
              <h2 className="text-3xl font-bold text-green-300 mb-1">
                ✅ Card Identified!
              </h2>
              <p className="text-slate-300 text-sm">
                Confidence: <span className="font-semibold text-green-300">
                  {(result.confidence * 100).toFixed(1)}%
                </span>
              </p>
            </div>
            <div className="text-right text-sm text-slate-400">
              <p>OCR: {(result.ocr_confidence * 100).toFixed(1)}%</p>
              <p>Match: {result.match_score}</p>
            </div>
          </div>
        </div>

        <div className="grid md:grid-cols-2 gap-6">
          {/* Card Image */}
          {result.image_url && (
            <div className="rounded-xl overflow-hidden bg-slate-800 aspect-video flex items-center justify-center">
              <img
                src={result.image_url}
                alt={result.name}
                className="w-full h-full object-cover"
                onError={(e) => {
                  e.target.src = 'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjYwMCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48cmVjdCB3aWR0aD0iNDAwIiBoZWlnaHQ9IjYwMCIgZmlsbD0iIzMzMzMzMyIvPjwvc3ZnPg==';
                }}
              />
            </div>
          )}

          {/* Card Details */}
          <div className="space-y-4">
            <div>
              <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                Card Name
              </h3>
              <p className="text-2xl font-bold text-white">{result.name}</p>
            </div>

            {result.type && (
              <div>
                <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                  Type
                </h3>
                <p className="text-white">{result.type}</p>
              </div>
            )}

            <div className="grid grid-cols-2 gap-4">
              {result.atk !== undefined && (
                <div>
                  <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                    ATK
                  </h3>
                  <p className="text-xl font-bold text-red-400">{result.atk}</p>
                </div>
              )}

              {result.def !== undefined && (
                <div>
                  <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                    DEF
                  </h3>
                  <p className="text-xl font-bold text-blue-400">{result.def}</p>
                </div>
              )}

              {result.level && (
                <div>
                  <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                    Level
                  </h3>
                  <p className="text-lg font-bold text-yellow-400">⭐ {result.level}</p>
                </div>
              )}

              {result.attribute && (
                <div>
                  <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                    Attribute
                  </h3>
                  <p className="text-white">{result.attribute}</p>
                </div>
              )}
            </div>

            {result.race && (
              <div>
                <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-1">
                  Race
                </h3>
                <p className="text-white">{result.race}</p>
              </div>
            )}
          </div>
        </div>

        {/* Description */}
        {result.description && (
          <div className="bg-slate-800 rounded-xl p-4">
            <h3 className="text-slate-400 text-xs font-mono uppercase tracking-wide mb-3">
              Description
            </h3>
            <p className="text-slate-300 text-sm leading-relaxed">
              {result.description}
              {result.description.length >= 500 && '...'}
            </p>
          </div>
        )}

        <button
          onClick={onRetry}
          className="w-full px-4 py-3 rounded-lg bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white font-semibold transition-all active:scale-95"
        >
          Scan Another Card
        </button>
      </div>
    );
  }

  return null;
}

function CardCandidate({ card, rank }) {
  return (
    <div className="bg-slate-800 rounded-xl p-4 border border-slate-700 hover:border-slate-600 transition-colors">
      <div className="flex gap-4">
        {card.image_url && (
          <img
            src={card.image_url}
            alt={card.name}
            className="w-24 h-32 object-cover rounded-lg flex-shrink-0"
            onError={(e) => {
              e.target.style.display = 'none';
            }}
          />
        )}

        <div className="flex-1">
          <div className="flex items-start justify-between mb-2">
            <div>
              <span className="text-slate-500 text-sm">#{rank}</span>
              <h4 className="text-white font-semibold text-lg">{card.name}</h4>
            </div>
            <span className="text-yellow-400 font-semibold">
              {(card.confidence * 100).toFixed(1)}%
            </span>
          </div>

          {card.type && (
            <p className="text-slate-400 text-sm mb-2">{card.type}</p>
          )}

          {card.description && (
            <p className="text-slate-400 text-sm line-clamp-2">
              {card.description}
            </p>
          )}
        </div>
      </div>
    </div>
  );
}

export default ResultDisplay;
