import React from 'react';
import { ExternalLink, Globe, Search, Bot } from 'lucide-react';

export interface Source {
  title: string;
  url: string;
  snippet?: string;
  domain?: string;
  type?: 'web' | 'perplexity' | 'openai' | 'search';
  position?: number;
  timestamp?: string;
  query?: string;
  model?: string;
}

interface SourceCardProps {
  source: Source;
  showSnippet?: boolean;
  compact?: boolean;
}

const getSourceIcon = (type: string) => {
  switch (type) {
    case 'web':
    case 'search':
      return <Search className="w-4 h-4" />;
    case 'perplexity':
      return <Globe className="w-4 h-4" />;
    case 'openai':
      return <Bot className="w-4 h-4" />;
    default:
      return <ExternalLink className="w-4 h-4" />;
  }
};

const getSourceColor = (type: string) => {
  switch (type) {
    case 'web':
    case 'search':
      return 'text-blue-400';
    case 'perplexity':
      return 'text-green-400';
    case 'openai':
      return 'text-purple-400';
    default:
      return 'text-gray-400';
  }
};

export default function SourceCard({ source, showSnippet = true, compact = false }: SourceCardProps) {
  const handleClick = () => {
    window.open(source.url, '_blank', 'noopener,noreferrer');
  };

  if (compact) {
    return (
      <div 
        onClick={handleClick}
        className="inline-flex items-center gap-2 px-3 py-1 bg-gray-800/50 hover:bg-gray-700/50 rounded-full cursor-pointer transition-colors group"
      >
        <span className={`${getSourceColor(source.type || 'web')}`}>
          {getSourceIcon(source.type || 'web')}
        </span>
        <span className="text-sm text-gray-300 group-hover:text-white truncate max-w-[200px]">
          {source.domain || new URL(source.url).hostname}
        </span>
        {source.position && (
          <span className="text-xs text-gray-500 bg-gray-700 px-2 py-0.5 rounded">
            #{source.position}
          </span>
        )}
      </div>
    );
  }

  return (
    <div 
      onClick={handleClick}
      className="bg-gray-800/30 hover:bg-gray-700/30 rounded-lg p-4 cursor-pointer transition-all duration-200 border border-gray-700/50 hover:border-gray-600/50 group"
    >
      <div className="flex items-start gap-3">
        <div className={`mt-1 ${getSourceColor(source.type || 'web')}`}>
          {getSourceIcon(source.type || 'web')}
        </div>
        
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-2">
            <h4 className="font-medium text-white group-hover:text-[#0CF2A0] transition-colors line-clamp-2">
              {source.title}
            </h4>
            {source.position && (
              <span className="text-xs text-gray-500 bg-gray-700 px-2 py-1 rounded flex-shrink-0">
                Rank #{source.position}
              </span>
            )}
          </div>
          
          <div className="flex items-center gap-2 mb-2">
            <span className="text-sm text-gray-400 truncate">
              {source.domain || new URL(source.url).hostname}
            </span>
            <ExternalLink className="w-3 h-3 text-gray-500 flex-shrink-0" />
          </div>
          
          {showSnippet && source.snippet && (
            <p className="text-sm text-gray-300 line-clamp-3 leading-relaxed">
              {source.snippet}
            </p>
          )}
          
          {source.timestamp && (
            <div className="mt-2 text-xs text-gray-500">
              {new Date(source.timestamp).toLocaleDateString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}