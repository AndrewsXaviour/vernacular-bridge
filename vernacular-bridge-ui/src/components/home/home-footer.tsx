import React, { useState } from 'react';
import { Sparkles, ArrowRight, Users, Heart } from 'lucide-react';

interface HomeFooterProps {
  onTransform: (text: string) => void;
  isLoading: boolean;
}

export default function HomeFooter({ onTransform, isLoading }: HomeFooterProps) {
  const [input, setInput] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onTransform(input);
    }
  };

  const demos = [
    "ஒளிச்சேர்க்கை என்றால் என்ன?",
    "What is supply and demand?",
    "GDP என்றால் என்ன?"
  ];

  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-8 font-sans pb-16">
      <div className="flex flex-col md:flex-row gap-6 items-stretch">
        
        {/* Left Side: Inline Input Panel */}
        <div className="flex-grow md:w-2/3 bg-white rounded-2xl border border-slate-200 p-8 shadow-sm flex flex-col justify-center">
          <div className="flex items-center space-x-2 mb-2">
            <Sparkles className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-bold text-slate-900">Try a concept</h2>
          </div>
          <p className="text-xs text-slate-500 font-medium mb-6">
            Type in Tamil or Tanglish. We&apos;ll explain in Tamil and Academic English.
          </p>

          <form onSubmit={handleSubmit} className="relative flex items-center mb-4">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="உதாரணம்: ஒளிச்சேர்க்கை என்றால் என்ன? / photosynthesis na enna?"
              className="w-full bg-slate-50 border border-slate-200 rounded-xl py-4 pl-4 pr-32 text-sm focus:outline-none focus:ring-2 focus:ring-blue-100 focus:border-blue-400 transition-all text-slate-800 placeholder:text-slate-400"
              disabled={isLoading}
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="absolute right-2 top-2 bottom-2 bg-blue-600 hover:bg-blue-700 text-white px-6 rounded-lg font-bold text-sm flex items-center space-x-2 transition-colors disabled:opacity-50"
            >
              <span>Explain</span>
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          <div className="flex items-center space-x-2 overflow-x-auto whitespace-nowrap pb-1 scrollbar-hide">
             <span className="text-[11px] font-bold text-blue-600">Examples:</span>
             {demos.map((demo, idx) => (
               <React.Fragment key={idx}>
                 <button 
                   onClick={() => setInput(demo)}
                   type="button"
                   className="text-[11px] text-slate-500 hover:text-slate-800 font-medium transition-colors"
                 >
                   {demo}
                 </button>
                 {idx < demos.length - 1 && <span className="text-slate-300 text-[10px]">•</span>}
               </React.Fragment>
             ))}
          </div>
        </div>

        {/* Right Side: Built For You Card */}
        <div className="md:w-1/3 bg-[#f0f7ff] rounded-2xl border border-[#cce4ff] p-8 shadow-sm flex flex-col justify-between">
           <div>
             <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center text-blue-600 mb-6">
               <Users className="w-6 h-6" />
             </div>
             <h3 className="text-sm font-bold text-slate-900 mb-2">Built for you</h3>
             <p className="text-xs text-slate-700 font-medium leading-relaxed">
               First-generation college students like you, who think in Tamil and aspire in English.
             </p>
           </div>
           
           <div className="mt-8 pt-4 border-t border-blue-200/50 flex items-center space-x-2">
              <Heart className="w-4 h-4 text-blue-500" />
              <span className="text-xs font-bold text-blue-700">You're not alone. We've got your back.</span>
           </div>
        </div>

      </div>
    </div>
  );
}
