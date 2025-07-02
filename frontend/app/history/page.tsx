"use client";

import React from "react";
import { motion } from "framer-motion";
import { MiniNavbar } from "@/components/Header";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useQuery } from "convex/react";
import { api } from "@/convex/_generated/api_cjs.cjs";
import { convex } from "@/lib/convex";
import { Calendar, BarChart3, Users, ExternalLink } from "lucide-react";
import { cn } from "@/lib/utils";

interface Analysis {
  _id: string;
  brand_name: string;
  analysis_timestamp: number;
  status: "pending" | "completed" | "failed";
  type: "brand" | "geo";
  competitors?: string[];
  sources?: any[];
}

function AnalysisCard({ analysis }: { analysis: Analysis }) {
  const date = new Date(analysis.analysis_timestamp).toLocaleDateString();
  const time = new Date(analysis.analysis_timestamp).toLocaleTimeString();

  const statusColors = {
    completed: "bg-green-500/20 text-green-400 border-green-500/30",
    pending: "bg-yellow-500/20 text-yellow-400 border-yellow-500/30",
    failed: "bg-red-500/20 text-red-400 border-red-500/30",
  };

  const typeColors = {
    brand: "bg-blue-500/20 text-blue-400 border-blue-500/30",
    geo: "bg-purple-500/20 text-purple-400 border-purple-500/30",
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="bg-gray-800/30 rounded-lg border border-gray-700/50 p-4 hover:border-gray-600/50 transition-colors"
    >
      <div className="flex items-start justify-between mb-3">
        <div>
          <h3 className="font-semibold text-white text-lg">{analysis.brand_name}</h3>
          <div className="flex items-center gap-2 mt-1">
            <Calendar className="w-4 h-4 text-gray-400" />
            <span className="text-sm text-gray-400">{date} at {time}</span>
          </div>
        </div>
        
        <div className="flex items-center gap-2">
          <span className={cn(
            "px-2 py-1 rounded-full text-xs font-medium border",
            typeColors[analysis.type]
          )}>
            {analysis.type === "brand" ? "Brand Analysis" : "GEO Analysis"}
          </span>
          <span className={cn(
            "px-2 py-1 rounded-full text-xs font-medium border",
            statusColors[analysis.status]
          )}>
            {analysis.status}
          </span>
        </div>
      </div>

      {analysis.competitors && analysis.competitors.length > 0 && (
        <div className="flex items-center gap-2 mb-3">
          <Users className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300">
            {analysis.competitors.length} competitors analyzed
          </span>
          <div className="flex flex-wrap gap-1">
            {analysis.competitors.slice(0, 3).map((competitor) => (
              <span 
                key={competitor}
                className="text-xs bg-gray-700 px-2 py-0.5 rounded text-gray-300"
              >
                {competitor}
              </span>
            ))}
            {analysis.competitors.length > 3 && (
              <span className="text-xs text-gray-500">
                +{analysis.competitors.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {analysis.sources && analysis.sources.length > 0 && (
        <div className="flex items-center gap-2 mb-3">
          <ExternalLink className="w-4 h-4 text-gray-400" />
          <span className="text-sm text-gray-300">
            {analysis.sources.length} sources referenced
          </span>
        </div>
      )}

      <div className="flex items-center justify-between mt-4">
        <button
          onClick={() => {
            // TODO: Navigate to analysis details
            console.log("View analysis:", analysis._id);
          }}
          className="text-sm text-[#0CF2A0] hover:text-[#0CF2A0]/80 transition-colors"
        >
          View Details →
        </button>
        
        <div className="flex items-center gap-2 text-xs text-gray-500">
          <BarChart3 className="w-3 h-3" />
          Analysis #{analysis._id.slice(-6)}
        </div>
      </div>
    </motion.div>
  );
}

export default function HistoryPage() {
  const { user, isAuthenticated, isLoading } = convex ? useCurrentUser() : { user: null, isAuthenticated: false, isLoading: false };
  const userAnalyses = convex && isAuthenticated ? 
    useQuery(api.users.getUserAnalyses, { limit: 20 }) : 
    null;

  if (!convex) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <MiniNavbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold mb-4">Analysis History</h1>
            <p className="text-gray-400">
              Analysis history requires Convex configuration.
            </p>
          </div>
        </div>
      </div>
    );
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <MiniNavbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center">
            <div className="w-8 h-8 bg-[#0CF2A0] rounded-full animate-pulse mx-auto mb-4"></div>
            <p className="text-gray-400">Loading your analysis history...</p>
          </div>
        </div>
      </div>
    );
  }

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-black text-white flex flex-col">
        <MiniNavbar />
        <div className="flex-1 flex items-center justify-center">
          <div className="text-center max-w-md">
            <h1 className="text-3xl font-bold mb-4">Analysis History</h1>
            <p className="text-gray-400 mb-6">
              Sign in to view your saved brand analyses and track your research progress.
            </p>
            <div className="p-4 bg-gray-800/30 rounded-lg border border-gray-700/50">
              <p className="text-sm text-gray-300">
                Your analysis history includes:
              </p>
              <ul className="mt-2 text-sm text-gray-400 space-y-1">
                <li>• Brand analysis results</li>
                <li>• Competitor research data</li>
                <li>• Source references and citations</li>
                <li>• GEO optimization insights</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
    );
  }

  const analyses = userAnalyses || [];

  return (
    <div className="min-h-screen bg-black text-white">
      <MiniNavbar />
      
      <div className="container mx-auto px-4 pt-20 pb-8">
        <div className="max-w-4xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-2">Analysis History</h1>
            <p className="text-gray-400">
              Your complete brand research and analysis archive
            </p>
          </div>

          {/* User Stats */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
            <div className="bg-gray-800/30 rounded-lg border border-gray-700/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Total Analyses</p>
                  <p className="text-2xl font-bold text-white">{user?.analysis_count || 0}</p>
                </div>
                <BarChart3 className="w-8 h-8 text-[#0CF2A0]" />
              </div>
            </div>
            
            <div className="bg-gray-800/30 rounded-lg border border-gray-700/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Recent Analyses</p>
                  <p className="text-2xl font-bold text-white">{analyses.length}</p>
                </div>
                <Calendar className="w-8 h-8 text-[#0CF2A0]" />
              </div>
            </div>
            
            <div className="bg-gray-800/30 rounded-lg border border-gray-700/50 p-4">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-400">Account Type</p>
                  <p className="text-lg font-bold text-[#0CF2A0] uppercase">
                    {user?.subscription_status || "FREE"}
                  </p>
                </div>
                <Users className="w-8 h-8 text-[#0CF2A0]" />
              </div>
            </div>
          </div>

          {/* Analysis List */}
          {analyses.length === 0 ? (
            <div className="text-center py-12">
              <BarChart3 className="w-16 h-16 text-gray-600 mx-auto mb-4" />
              <h3 className="text-xl font-semibold text-white mb-2">No analyses yet</h3>
              <p className="text-gray-400 mb-6">
                Start your first brand analysis to see your history here.
              </p>
              <motion.a
                href="/analysis"
                className="inline-block bg-[#0CF2A0] text-black font-semibold py-2 px-6 rounded-lg hover:bg-opacity-90 transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                Start Analysis
              </motion.a>
            </div>
          ) : (
            <div className="space-y-4">
              <h2 className="text-xl font-semibold text-white mb-4">
                Recent Analyses ({analyses.length})
              </h2>
              {analyses.map((analysis) => (
                <AnalysisCard key={analysis._id} analysis={analysis} />
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}