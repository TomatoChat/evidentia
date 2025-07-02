import React, { useState } from 'react';
import { Filter, ChevronDown, ChevronUp } from 'lucide-react';
import SourceCard, { Source } from './SourceCard';

interface SourceListProps {
  sources: Source[];
  title?: string;
  showFilter?: boolean;
  compact?: boolean;
  maxVisible?: number;
}

const sourceTypeLabels = {
  web: 'Web Search',
  search: 'Search Results',
  perplexity: 'Perplexity AI',
  openai: 'OpenAI Web',
  all: 'All Sources'
};

export default function SourceList({ 
  sources, 
  title = "Sources", 
  showFilter = true, 
  compact = false,
  maxVisible = 5 
}: SourceListProps) {
  const [selectedType, setSelectedType] = useState<string>('all');
  const [expanded, setExpanded] = useState(false);

  if (!sources || sources.length === 0) {
    return null;
  }

  // Filter sources by type
  const filteredSources = selectedType === 'all' 
    ? sources 
    : sources.filter(source => source.type === selectedType);

  // Get unique source types
  const availableTypes = Array.from(new Set(sources.map(source => source.type || 'web')));

  // Handle visibility
  const visibleSources = expanded ? filteredSources : filteredSources.slice(0, maxVisible);
  const hasMore = filteredSources.length > maxVisible;

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          {title}
          <span className="text-sm text-gray-400 bg-gray-700/50 px-2 py-1 rounded">
            {filteredSources.length}
          </span>
        </h3>
        
        {showFilter && availableTypes.length > 1 && (
          <div className="flex items-center gap-2">
            <Filter className="w-4 h-4 text-gray-400" />
            <select
              value={selectedType}
              onChange={(e) => setSelectedType(e.target.value)}
              className="bg-gray-800 border border-gray-600 rounded-lg px-3 py-1 text-sm text-white focus:outline-none focus:border-[#0CF2A0]"
            >
              <option value="all">{sourceTypeLabels.all}</option>
              {availableTypes.map(type => (
                <option key={type} value={type}>
                  {sourceTypeLabels[type as keyof typeof sourceTypeLabels] || type}
                </option>
              ))}
            </select>
          </div>
        )}
      </div>

      <div className={compact ? "flex flex-wrap gap-2" : "space-y-3"}>
        {visibleSources.map((source, index) => (
          <SourceCard 
            key={`${source.url}-${index}`} 
            source={source} 
            compact={compact}
            showSnippet={!compact}
          />
        ))}
      </div>

      {hasMore && (
        <button
          onClick={() => setExpanded(!expanded)}
          className="flex items-center gap-2 text-sm text-gray-400 hover:text-[#0CF2A0] transition-colors"
        >
          {expanded ? (
            <>
              <ChevronUp className="w-4 h-4" />
              Show Less
            </>
          ) : (
            <>
              <ChevronDown className="w-4 h-4" />
              Show {filteredSources.length - maxVisible} More Sources
            </>
          )}
        </button>
      )}
    </div>
  );
}