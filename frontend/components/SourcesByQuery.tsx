import React, { useState } from 'react';
import { ChevronDown, ChevronRight, Search, Bot, Globe } from 'lucide-react';
import { Source } from './SourceCard';
import SourceList from './SourceList';

interface SourcesByQueryProps {
  sources: Source[];
  queries?: Array<{ topic?: string; prompt?: string; query?: string }>;
}

interface GroupedSources {
  [key: string]: {
    query: string;
    sources: Source[];
    models: string[];
  };
}

export default function SourcesByQuery({ sources, queries }: SourcesByQueryProps) {
  const [expandedQueries, setExpandedQueries] = useState<Set<string>>(new Set());

  if (!sources || sources.length === 0) {
    return null;
  }

  // Group sources by query
  const groupedSources: GroupedSources = {};
  
  sources.forEach(source => {
    const queryKey = source.query || 'general';
    if (!groupedSources[queryKey]) {
      groupedSources[queryKey] = {
        query: queryKey,
        sources: [],
        models: []
      };
    }
    groupedSources[queryKey].sources.push(source);
    if (source.model && !groupedSources[queryKey].models.includes(source.model)) {
      groupedSources[queryKey].models.push(source.model);
    }
  });

  const toggleQuery = (queryKey: string) => {
    const newExpanded = new Set(expandedQueries);
    if (newExpanded.has(queryKey)) {
      newExpanded.delete(queryKey);
    } else {
      newExpanded.add(queryKey);
    }
    setExpandedQueries(newExpanded);
  };

  // Group sources by type for overview
  const sourcesByType = sources.reduce((acc, source) => {
    const type = source.type || 'web';
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="space-y-6">
      {/* Overview Stats */}
      <div className="bg-gray-800/30 rounded-lg p-4 border border-gray-700/50">
        <h3 className="text-lg font-semibold text-white mb-3">Source Overview</h3>
        <div className="flex flex-wrap gap-4">
          <div className="flex items-center gap-2">
            <Search className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-gray-300">
              Total Sources: <span className="text-white font-medium">{sources.length}</span>
            </span>
          </div>
          <div className="flex items-center gap-2">
            <Globe className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">
              Queries: <span className="text-white font-medium">{Object.keys(groupedSources).length}</span>
            </span>
          </div>
          {Object.entries(sourcesByType).map(([type, count]) => (
            <div key={type} className="flex items-center gap-2">
              <Bot className="w-4 h-4 text-purple-400" />
              <span className="text-sm text-gray-300">
                {type}: <span className="text-white font-medium">{count}</span>
              </span>
            </div>
          ))}
        </div>
      </div>

      {/* Sources by Query */}
      <div className="space-y-4">
        <h3 className="text-lg font-semibold text-white">Sources by Query</h3>
        
        {Object.entries(groupedSources).map(([queryKey, group]) => {
          const isExpanded = expandedQueries.has(queryKey);
          
          return (
            <div key={queryKey} className="bg-gray-800/30 rounded-lg border border-gray-700/50 overflow-hidden">
              <button
                onClick={() => toggleQuery(queryKey)}
                className="w-full p-4 text-left hover:bg-gray-700/30 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-400" />
                    )}
                    <div>
                      <h4 className="font-medium text-white line-clamp-1">
                        {group.query === 'general' ? 'General Search' : group.query}
                      </h4>
                      <div className="flex items-center gap-4 mt-1">
                        <span className="text-sm text-gray-400">
                          {group.sources.length} sources
                        </span>
                        {group.models.length > 0 && (
                          <span className="text-sm text-gray-500">
                            Models: {group.models.join(', ')}
                          </span>
                        )}
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {group.sources.slice(0, 3).map((source, index) => {
                      const domain = source.domain || (source.url ? new URL(source.url).hostname : '');
                      return (
                        <div
                          key={index}
                          className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300"
                          title={source.title}
                        >
                          {domain}
                        </div>
                      );
                    })}
                    {group.sources.length > 3 && (
                      <div className="text-xs bg-gray-700 px-2 py-1 rounded text-gray-300">
                        +{group.sources.length - 3}
                      </div>
                    )}
                  </div>
                </div>
              </button>
              
              {isExpanded && (
                <div className="p-4 pt-0 border-t border-gray-700/30">
                  <SourceList
                    sources={group.sources}
                    showFilter={true}
                    compact={false}
                    maxVisible={10}
                  />
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}