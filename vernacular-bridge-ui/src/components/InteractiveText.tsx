'use client';

import React, { useState, useCallback, useRef, useEffect } from 'react';
import { LearningEngine } from '@/utils/learning-engine';

interface InteractiveTextProps {
  text: string;
  isTamil?: boolean;
}

export default function InteractiveText({ text, isTamil }: InteractiveTextProps) {
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const hideTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const handleMouseEnter = useCallback((index: number) => {
    // Clear any pending hide timeout
    if (hideTimeoutRef.current) {
      clearTimeout(hideTimeoutRef.current);
      hideTimeoutRef.current = null;
    }
    setHoveredIndex(index);
  }, []);

  const handleMouseLeave = useCallback(() => {
    // Add a small delay before hiding to prevent flicker when moving between elements
    hideTimeoutRef.current = setTimeout(() => {
      setHoveredIndex(null);
    }, 100);
  }, []);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (hideTimeoutRef.current) {
        clearTimeout(hideTimeoutRef.current);
      }
    };
  }, []);

  if (!text) return null;

  const words = text.split(/(\s+)/);

  return (
    <span className={isTamil ? "tamil-font" : "academic-font"}>
      {words.map((word, index) => {
        const tooltip = LearningEngine.getTooltip(word);
        const shouldHighlight = !!tooltip || /^[A-Z][a-z]+/.test(word.trim());

        if (shouldHighlight) {
          const isHovered = hoveredIndex === index;

          return (
            <span
              key={index}
              className="relative inline-block"
              onMouseEnter={() => handleMouseEnter(index)}
              onMouseLeave={handleMouseLeave}
            >
              <span
                className={`
                  cursor-help transition-all duration-300
                  ${isTamil
                    ? `border-b-2 ${isHovered ? 'border-teal-500' : 'border-teal-200'}`
                    : `text-[#0f766e] font-bold underline underline-offset-4 ${isHovered ? 'decoration-[#0f766e]' : 'decoration-teal-200'}`
                  }
                `}
              >
                {word}
              </span>

              {/* Tooltip Overlay - positioned to avoid overlapping other words */}
              <div
                className={`absolute left-1/2 -translate-x-1/2 mb-3 w-48 pointer-events-none transition-all duration-200 z-50 ${
                  isHovered
                    ? 'opacity-100 translate-y-0 bottom-full'
                    : 'opacity-0 translate-y-2 bottom-full'
                }`}
                style={{ 
                  // Ensure tooltip doesn't extend beyond viewport
                  maxHeight: '200px',
                  overflow: 'visible'
                }}
              >
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
