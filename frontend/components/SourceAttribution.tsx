import React from 'react';
import { Source } from './SourceCard';
import SourceList from './SourceList';

interface SourceAttributionProps {
  sources: Source[];
  inline?: boolean;
  showTitle?: boolean;
  compact?: boolean;
}

export default function SourceAttribution({ 
  sources, 
  inline = false, 
  showTitle = true,
  compact = false 
}: SourceAttributionProps) {
  if (!sources || sources.length === 0) {
    return null;
  }

  if (inline) {
    return (
      <div className="inline-flex flex-wrap gap-1 items-center">
        <span className="text-xs text-gray-500 mr-1">Sources:</span>
        {sources.slice(0, 3).map((source, index) => (
          <button
            key={`${source.url}-${index}`}
            onClick={() => window.open(source.url, '_blank', 'noopener,noreferrer')}
            className="text-xs text-blue-400 hover:text-blue-300 underline hover:no-underline"
          >
            [{index + 1}]
          </button>
        ))}
        {sources.length > 3 && (
          <span className="text-xs text-gray-500">
            +{sources.length - 3} more
          </span>
        )}
      </div>
    );
  }

  return (
    <div className="mt-6 p-4 bg-gray-900/50 rounded-lg border border-gray-700/50">
      <SourceList 
        sources={sources}
        title={showTitle ? "Sources & References" : undefined}
        compact={compact}
        maxVisible={compact ? 10 : 5}
      />
    </div>
  );
}