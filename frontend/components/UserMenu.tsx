"use client";

import React, { useState } from "react";
import { useAuthActions } from "@convex-dev/auth/react";
import { User, LogOut, History, Settings, ChevronDown } from "lucide-react";

interface UserMenuProps {
  user: {
    name?: string;
    email?: string;
    image?: string;
    analysis_count?: number;
    subscription_status?: "free" | "pro" | "enterprise";
  };
}

export function UserMenu({ user }: UserMenuProps) {
  const { signOut } = useAuthActions();
  const [isOpen, setIsOpen] = useState(false);

  return (
    <div className="relative">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="flex items-center gap-2 p-2 rounded-lg hover:bg-gray-800 transition-colors"
      >
        {user.image ? (
          <img
            src={user.image}
            alt={user.name || user.email}
            className="w-8 h-8 rounded-full"
          />
        ) : (
          <div className="w-8 h-8 bg-gray-700 rounded-full flex items-center justify-center">
            <User className="w-4 h-4 text-gray-300" />
          </div>
        )}
        <div className="hidden sm:block text-left">
          <div className="text-sm font-medium text-white">
            {user.name || user.email}
          </div>
          <div className="text-xs text-gray-400">
            {user.subscription_status || "free"} • {user.analysis_count || 0} analyses
          </div>
        </div>
        <ChevronDown className="w-4 h-4 text-gray-400" />
      </button>

      {isOpen && (
        <>
          <div
            className="fixed inset-0 z-10"
            onClick={() => setIsOpen(false)}
          />
          <div className="absolute right-0 mt-2 w-64 bg-gray-900 border border-gray-700 rounded-lg shadow-lg z-20">
            <div className="p-3 border-b border-gray-700">
              <div className="text-sm font-medium text-white">
                {user.name || "Anonymous"}
              </div>
              <div className="text-xs text-gray-400">{user.email}</div>
              <div className="text-xs text-[#0CF2A0] mt-1">
                {user.subscription_status?.toUpperCase() || "FREE"} PLAN
              </div>
            </div>

            <div className="py-1">
              <a
                href="/history"
                onClick={() => setIsOpen(false)}
                className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <History className="w-4 h-4" />
                Analysis History
                <span className="ml-auto text-xs bg-gray-700 px-2 py-0.5 rounded">
                  {user.analysis_count || 0}
                </span>
              </a>

              <button
                onClick={() => {
                  setIsOpen(false);
                  // TODO: Navigate to settings
                }}
                className="flex items-center gap-3 w-full px-3 py-2 text-sm text-gray-300 hover:bg-gray-800 hover:text-white"
              >
                <Settings className="w-4 h-4" />
                Settings
              </button>
            </div>

            <div className="border-t border-gray-700 py-1">
              <button
                onClick={() => {
                  signOut();
                  setIsOpen(false);
                }}
                className="flex items-center gap-3 w-full px-3 py-2 text-sm text-red-400 hover:bg-gray-800"
              >
                <LogOut className="w-4 h-4" />
                Sign Out
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}