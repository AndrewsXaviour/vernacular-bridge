import React from 'react';
import { BookOpen, Award } from 'lucide-react';
import InteractiveText from '../InteractiveText';

interface EnglishCardProps {
  content?: string;
}

export default function EnglishCard({ content }: EnglishCardProps) {
  return (
    <div className="bg-white rounded-[2.5rem] border border-gray-100 border-l-[6px] border-l-indigo-600 p-12 shadow-sm transition-all duration-300 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-indigo-50/50 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-indigo-100/50 transition-colors" />
      
      <div className="flex items-center justify-between mb-10 relative z-10">
        <div className="flex items-center space-x-4">
          <div className="bg-indigo-600/10 p-3 rounded-2xl">
            <BookOpen className="w-6 h-6 text-indigo-600" />
          </div>
          <div>
            <h3 className="text-xl font-black text-gray-900 tracking-tight">Academic Narrative</h3>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Formal Linguistic Synthesis</p>
          </div>
        </div>

        <div className="flex items-center space-x-2 px-4 py-2 bg-indigo-50 rounded-xl border border-indigo-100">
          <Award className="w-3.5 h-3.5 text-indigo-600" />
          <span className="text-[10px] font-black text-indigo-700 uppercase tracking-widest">Precision Level: Advanced</span>
        </div>
      </div>
      
      <div className="relative z-10">
        <div className="prose prose-indigo max-w-none">
          <div className="text-lg md:text-[1.15rem] leading-[1.9] text-[#1e293b] whitespace-pre-wrap font-serif italic text-justify">
            {content ? (
              <InteractiveText text={content} />
            ) : (
              <div className="space-y-4">
                <div className="h-4 bg-gray-50 rounded-full w-full animate-pulse" />
                <div className="h-4 bg-gray-50 rounded-full w-[85%] animate-pulse" />
                <div className="h-4 bg-gray-50 rounded-full w-[95%] animate-pulse" />
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="mt-12 pt-8 border-t border-gray-50 flex items-center justify-between relative z-10">
        <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest">Linguistic Metrics</div>
        <div className="flex space-x-6">
          <div className="flex flex-col items-center">
            <span className="text-sm font-black text-indigo-600">85%</span>
            <span className="text-[8px] font-bold text-gray-400 uppercase tracking-tighter">Vocabulary Density</span>
          </div>
          <div className="flex flex-col items-center">
            <span className="text-sm font-black text-indigo-600">Complex</span>
            <span className="text-[8px] font-bold text-gray-400 uppercase tracking-tighter">Sentence Structure</span>
          </div>
        </div>
      </div>
    </div>
  );
}
