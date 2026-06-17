'use client';

import React from 'react';
import { LearningEngine } from '@/utils/learning-engine';
import { motion, AnimatePresence } from 'framer-motion';

interface InteractiveTextProps {
  text: string;
  isTamil?: boolean;
}

export default function InteractiveText({ text, isTamil }: InteractiveTextProps) {
  if (!text) return null;

  // Simple regex to find technical/academic terms
  // We look for capitalized words or words from our fallback list
  const words = text.split(/(\s+)/);

  return (
    <span className={isTamil ? "tamil-font" : "academic-font"}>
      {words.map((word, index) => {
        const tooltip = LearningEngine.getTooltip(word);
        const shouldHighlight = !!tooltip || /^[A-Z][a-z]+/.test(word.trim());

        if (shouldHighlight) {
          return (
            <span key={index} className="relative group inline-block">
              <span className={`
                cursor-help transition-all duration-300
                ${isTamil ? 'border-b-2 border-teal-200 hover:border-teal-500' : 'text-[#0f766e] font-bold underline decoration-teal-200 underline-offset-4 hover:decoration-[#0f766e]'}
              `}>
                {word}
              </span>
              
              {/* Tooltip Overlay */}
              <div className="absolute bottom-full left-1/2 -translate-x-1/2 mb-3 w-48 opacity-0 group-hover:opacity-100 pointer-events-none transition-all duration-300 translate-y-2 group-hover:translate-y-0 z-50">
                <div className="bg-[#0f172a] text-white p-3 rounded-xl shadow-2xl text-[10px] leading-relaxed border border-white/10 relative">
                  <div className="font-black text-teal-400 uppercase tracking-widest mb-1 border-b border-white/5 pb-1">
                    {word.replace(/[^a-zA-Z]/g, '') || "Academic Term"}
                  </div>
                  {tooltip || "Key academic terminology detected by Vernacular Bridge engine."}
                  <div className="absolute top-full left-1/2 -translate-x-1/2 border-8 border-transparent border-t-[#0f172a]" />
                </div>
              </div>
            </span>
          );
        }

        return <span key={index}>{word}</span>;
      })}
    </span>
  );
}
