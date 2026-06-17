import React, { useState } from 'react';
import { Languages, Zap } from 'lucide-react';
import InteractiveText from '../InteractiveText';

interface TamilCardProps {
  content?: string;
}

export default function TamilCard({ content }: TamilCardProps) {
  const [isSimplified, setIsSimplified] = useState(false);

  return (
    <div className="bg-white rounded-[2.5rem] border border-gray-100 border-l-[6px] border-l-[#0f766e] p-12 shadow-sm transition-all duration-300 relative overflow-hidden group">
      <div className="absolute top-0 right-0 w-32 h-32 bg-teal-50/50 rounded-full -mr-16 -mt-16 blur-3xl group-hover:bg-teal-100/50 transition-colors" />
      
      <div className="flex items-center justify-between mb-10 relative z-10">
        <div className="flex items-center space-x-4">
          <div className="bg-[#0f766e]/10 p-3 rounded-2xl">
            <Languages className="w-6 h-6 text-[#0f766e]" />
          </div>
          <div>
            <h3 className="text-xl font-black text-gray-900 tracking-tight">Vernacular Bridge</h3>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Simplifying Cognitive Entry</p>
          </div>
        </div>

        <button 
          onClick={() => setIsSimplified(!isSimplified)}
          className={`flex items-center space-x-2 px-4 py-2 rounded-xl border transition-all duration-300
            ${isSimplified ? 'bg-teal-600 border-teal-600 text-white shadow-lg' : 'bg-white border-gray-100 text-gray-500 hover:border-teal-200'}
          `}
        >
          <Zap className={`w-3.5 h-3.5 ${isSimplified ? 'fill-white' : ''}`} />
          <span className="text-[10px] font-black uppercase tracking-widest">ELI10 Engine</span>
        </button>
      </div>
      
      <div className="relative z-10">
        <div 
          className="tamil-font text-[#1a2e2c] font-medium leading-relaxed"
          style={{ 
            fontSize: '1.2rem', 
            lineHeight: '2.1',
            wordSpacing: '0.05em'
          }}
        >
          {content ? (
            <InteractiveText text={isSimplified ? "This is a simplified version of the explanation to make it even easier to understand. " + content : content} isTamil={true} />
          ) : (
            <div className="space-y-4">
              <div className="h-4 bg-gray-50 rounded-full w-full animate-pulse" />
              <div className="h-4 bg-gray-50 rounded-full w-[90%] animate-pulse" />
              <div className="h-4 bg-gray-50 rounded-full w-[95%] animate-pulse" />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
