import React from 'react';
import { Sparkles, RefreshCcw } from 'lucide-react';

interface InputPanelProps {
  onTransform: (text: string) => void;
  isLoading: boolean;
  demoMode?: boolean;
  initialValue?: string;
}

const demos = [
  "நீராவிக் அழுத்தம்", // Using the example from the mockup
  "Photosynthesis",
  "Budget Deficit",
  "Elasticity of Demand",
  "Blood Pressure"
];

export default function InputPanel({ onTransform, isLoading, demoMode, initialValue = "" }: InputPanelProps) {
  const [input, setInput] = React.useState(initialValue);

  const handleSubmit = (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (input.trim()) {
      onTransform(input);
    }
  };

  const handleClear = () => {
    setInput("");
  };

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm font-sans mb-6">
      
      {/* Header section with number */}
      <div className="flex items-center space-x-3 mb-4">
        <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">
          1
        </div>
        <div>
          <h2 className="text-sm font-bold text-slate-800">Enter your concept</h2>
          <p className="text-xs text-slate-500">Type in Tamil or Tanglish. We&apos;ll explain it step-by-step.</p>
        </div>
      </div>
      
      {/* Input area */}
      <div className="flex space-x-4 mb-4">
        <div className="flex-1 relative">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            className="w-full p-4 rounded-xl border border-slate-200 focus:ring-2 focus:ring-blue-100 focus:border-blue-400 resize-none text-sm text-slate-800 shadow-inner"
            rows={2}
            disabled={isLoading}
          />
          <div className="absolute bottom-3 right-3 text-[10px] text-slate-400 font-medium">
            {input.length}/500
          </div>
        </div>
        
        <div className="w-32 flex flex-col space-y-2">
          <button
            onClick={() => handleSubmit()}
            disabled={isLoading || !input.trim()}
            className="w-full bg-blue-600 text-white py-2.5 rounded-lg font-bold text-xs flex items-center justify-center space-x-2 hover:bg-blue-700 transition-colors disabled:opacity-50 disabled:cursor-not-allowed shadow-sm"
          >
            {isLoading ? (
              <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                <Sparkles className="w-3.5 h-3.5" />
                <span>Explain Concept</span>
              </>
            )}
          </button>
          
          <button
            onClick={handleClear}
            disabled={isLoading || !input.trim()}
            className="w-full text-slate-500 py-1.5 rounded-lg font-bold text-xs flex items-center justify-center space-x-1.5 hover:text-slate-700 hover:bg-slate-50 transition-colors disabled:opacity-50"
          >
            <RefreshCcw className="w-3 h-3" />
            <span>Clear</span>
          </button>
        </div>
      </div>
      
      {/* Demos */}
      <div className="flex items-center space-x-3">
        <span className="text-xs font-bold text-blue-600">Try these examples:</span>
        <div className="flex flex-wrap gap-2">
          {demos.map((demo) => (
            <button
              key={demo}
              type="button"
              onClick={() => setInput(demo)}
              disabled={isLoading}
              className="px-3 py-1 rounded-full bg-white text-slate-600 text-[11px] font-medium border border-slate-200 hover:border-slate-300 hover:text-slate-800 transition-colors"
            >
              {demo}
            </button>
          ))}
        </div>
      </div>

    </div>
  );
}
