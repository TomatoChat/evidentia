"use client";

import React from 'react';
import { motion } from "framer-motion";
import { MiniNavbar } from "@/components/Header";
import { cn } from "@/lib/utils";

const ManifestoCard = ({ 
  icon, 
  title, 
  content, 
  quote,
  index
}: { 
  icon: string; 
  title: string; 
  content: string; 
  quote?: string;
  index: number;
}) => (
  <motion.div 
    initial={{ opacity: 0, y: 50 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ duration: 0.6, delay: index * 0.1 }}
    className="min-w-[380px] max-w-[380px] md:min-w-[420px] md:max-w-[420px] h-[500px] bg-white/5 backdrop-blur-sm rounded-xl border border-white/10 p-8 flex flex-col justify-center relative transition-all duration-300 hover:bg-white/10 hover:border-white/20 hover:transform hover:-translate-y-2 group"
  >
    <div className="text-5xl text-center mb-6 opacity-80 group-hover:opacity-100 transition-opacity">
      {icon}
    </div>
    <h2 className="text-2xl font-bold mb-6 text-center text-white">
      {title}
    </h2>
    <div className="text-base leading-relaxed text-center text-gray-300 flex-grow flex items-center">
      <p>{content}</p>
    </div>
    {quote && (
      <div className="italic text-lg mt-6 p-4 bg-white/5 rounded-lg border-l-4 border-[#0CF2A0] text-gray-400">
        {quote}
      </div>
    )}
  </motion.div>
);

export default function ManifestoPage() {
  const manifestoCards = [
    {
      icon: "🎯",
      title: "Our Mission",
      content: "To revolutionize how brands understand their digital presence in the age of AI-powered search. We believe every business deserves to know exactly how they appear when customers ask AI assistants about their needs.",
      quote: "\"In a world where AI answers questions, being findable means being valuable.\""
    },
    {
      icon: "🔍",
      title: "The Problem",
      content: "Traditional SEO is dying. ChatGPT, Claude, and other AI assistants are becoming the new search engines, but businesses have no idea how their brand appears in AI responses. This invisible shift is happening right now, and most companies are flying blind.",
      quote: "\"If your brand isn't mentioned by AI, do you really exist?\""
    },
    {
      icon: "🚀",
      title: "Our Solution",
      content: "Evidentia provides deep AI search analysis, showing you exactly how your brand performs against competitors across hundreds of relevant queries. We reveal what AI systems really think about your business.",
      quote: "\"Knowledge is power. AI knowledge is the future.\""
    },
    {
      icon: "⚡",
      title: "Why Now?",
      content: "We're at the inflection point where AI search will dominate human behavior. The companies that optimize for AI discoverability today will own their market tomorrow. The time to act is now, not later.",
      quote: "\"The future belongs to those who prepare for it today.\""
    },
    {
      icon: "🌟",
      title: "Our Promise",
      content: "We democratize AI search insights for businesses of all sizes. No more guessing, no more hoping. Just clear, actionable data about your brand's AI presence and concrete steps to improve it.",
      quote: "\"Transparency breeds excellence.\""
    },
    {
      icon: "🔮",
      title: "The Vision",
      content: "A world where every business understands their AI footprint as clearly as their website analytics. Where brand visibility in AI responses is measured, optimized, and mastered by companies everywhere.",
      quote: "\"The future of search is AI. The future of AI search is Evidentia.\""
    }
  ];

  return (
    <div className={cn("flex w-full flex-col min-h-screen bg-black relative")}>
      {/* Subtle background gradient */}
      <div className="absolute inset-0 bg-gradient-to-br from-black via-gray-900/50 to-black" />
      
      {/* Content Layer */}
      <div className="relative z-10 flex flex-col flex-1">
        {/* Navigation */}
        <MiniNavbar />

        {/* Main content container */}
        <div className="flex flex-1 flex-col mt-20">
          {/* Header Section */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.8 }}
            className="text-center py-16 px-8"
          >
            <motion.h1 
              className="text-4xl md:text-6xl font-bold mb-6 text-white"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              Our <span className="text-[#0CF2A0]">Manifesto</span>
            </motion.h1>
            <motion.p 
              className="text-lg md:text-xl text-gray-400 max-w-3xl mx-auto leading-relaxed"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              The principles that drive our mission to democratize AI search insights 
              and empower businesses in the generative search era.
            </motion.p>
          </motion.div>

          {/* Scrollable Cards Container */}
          <div className="flex-1 overflow-x-auto overflow-y-hidden px-8 pb-16">
            <div className="flex gap-8 min-w-max">
              {manifestoCards.map((card, index) => (
                <ManifestoCard
                  key={index}
                  index={index}
                  icon={card.icon}
                  title={card.title}
                  content={card.content}
                  quote={card.quote}
                />
              ))}
            </div>
          </div>

          {/* Navigation Dots */}
          <div className="flex justify-center gap-3 py-8">
            {manifestoCards.map((_, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ duration: 0.3, delay: index * 0.05 + 0.8 }}
                className="w-2 h-2 rounded-full bg-white/30 cursor-pointer transition-all duration-300 hover:bg-[#0CF2A0] hover:scale-125"
              />
            ))}
          </div>

          {/* Footer/CTA Section */}
          <motion.div 
            initial={{ opacity: 0, y: 30 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 1.2 }}
            className="text-center py-16 px-8 bg-gradient-to-t from-gray-900/50 to-transparent"
          >
            <h2 className="text-2xl md:text-3xl font-bold mb-4 text-white">
              Ready to understand your AI presence?
            </h2>
            <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
              Join forward-thinking brands that are already optimizing for the AI search revolution.
            </p>
            <motion.a
              href="/"
              className="inline-flex items-center px-8 py-3 bg-[#0CF2A0] text-black font-semibold rounded-lg hover:bg-opacity-90 transition-all duration-200"
              whileHover={{ scale: 1.05, y: -2 }}
              whileTap={{ scale: 0.95 }}
            >
              Start Your Analysis
              <svg className="ml-2 w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
              </svg>
            </motion.a>
          </motion.div>
        </div>
      </div>
    </div>
  );
} 