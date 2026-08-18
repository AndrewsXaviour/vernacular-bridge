import React from 'react';
import { Volume2 } from 'lucide-react';
import InteractiveText from '../InteractiveText';

interface EnglishCardProps {
  content?: string;
}

export default function EnglishCard({ content }: EnglishCardProps) {
  // Placeholder key terms for UI demonstration
  const keyTerms = ['plant', 'sunlight', 'chlorophyll', 'glucose', 'oxygen'];

  return (
    <div className="bg-[#f0f7ff] rounded-2xl border border-[#cce4ff] p-5 shadow-sm font-sans flex flex-col h-full">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold text-[#1e5eb8]">Academic English</h3>
        <button className="text-[#1e5eb8] hover:bg-[#dbeafe] p-1.5 rounded-lg transition-colors">
          <Volume2 className="w-4 h-4" />
        </button>
      </div>
      
      <div className="flex-grow mb-6">
        <div className="text-slate-700 font-medium leading-relaxed text-sm text-justify">
          {content ? (
            <InteractiveText text={content} />
          ) : (
            <div className="space-y-3">
              <div className="h-3 bg-[#dbeafe] rounded-full w-full animate-pulse" />
              <div className="h-3 bg-[#dbeafe] rounded-full w-[85%] animate-pulse" />
              <div className="h-3 bg-[#dbeafe] rounded-full w-[95%] animate-pulse" />
            </div>
          )}
        </div>
      </div>
      
      <div className="mt-auto pt-4 border-t border-[#cce4ff] flex items-center space-x-2">
        <span className="text-xs font-bold text-[#1e5eb8]">Key terms:</span>
        <div className="flex flex-wrap gap-1">
          {keyTerms.map((term, i) => (
            <React.Fragment key={i}>
              <span className="text-xs text-[#1e5eb8]">{term}</span>
              {i < keyTerms.length - 1 && <span className="text-[#1e5eb8] text-xs">,</span>}
            </React.Fragment>
          ))}
        </div>
      </div>
    </div>
  );
}
