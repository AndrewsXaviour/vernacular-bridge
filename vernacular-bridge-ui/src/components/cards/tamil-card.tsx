import React from 'react';
import { Volume2 } from 'lucide-react';
import InteractiveText from '../InteractiveText';

interface TamilCardProps {
  content?: string;
}

export default function TamilCard({ content }: TamilCardProps) {
  // Placeholder key terms for UI demonstration
  const keyTerms = ['தாவரம்', 'சூரிய ஒளி', 'குளோரோபில்', 'குளுக்கோஸ்', 'ஆக்ஸிஜன்'];

  return (
    <div className="bg-[#f2fbf5] rounded-2xl border border-[#c6e9d2] p-5 shadow-sm font-sans flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#147a42]">Tamil (Simple Explanation)</h3>
        <button className="text-[#147a42] hover:bg-[#e0f4e8] p-1.5 rounded-lg transition-colors">
          <Volume2 className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex-grow mb-6">
        <div className="tamil-font text-slate-700 font-medium leading-relaxed text-sm">
          {content ? (
            <InteractiveText text={content} isTamil={true} />
          ) : (
            <div className="space-y-3">
              <div className="h-3 bg-[#e0f4e8] rounded-full w-full animate-pulse" />
              <div className="h-3 bg-[#e0f4e8] rounded-full w-[90%] animate-pulse" />
              <div className="h-3 bg-[#e0f4e8] rounded-full w-[95%] animate-pulse" />
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-auto pt-4 border-t border-[#c6e9d2] flex items-center space-x-2">
        <span className="text-xs font-bold text-[#147a42]">முக்கிய சொற்கள்:</span>
        <div className="flex flex-wrap gap-1">
          {keyTerms.map((term, i) => (
            <React.Fragment key={i}>
              <span className="text-xs text-[#147a42]">{term}</span>
              {i < keyTerms.length - 1 && <span className="text-[#147a42] text-xs">,</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
