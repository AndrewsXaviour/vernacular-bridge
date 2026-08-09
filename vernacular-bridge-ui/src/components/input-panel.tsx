import React from 'react';
import { Send, Lightbulb } from 'lucide-react';

interface InputPanelProps {
  onTransform: (text: string) => void;
  isLoading: boolean;
  demoMode?: boolean;
}

const demos = [
  "Photosynthesis",
  "Newton’s Laws",
  "Fractions",
  "Respiration",
  "Freedom Struggle"
];

export default function InputPanel({ onTransform, isLoading, demoMode }: InputPanelProps) {
  const [input, setInput] = React.useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (input.trim()) {
      onTransform(input);
    }
  };

  return (
    <div className="bg-white rounded-2xl shadow-sm border border-gray-100 p-6 h-full flex flex-col">
      <h2 className="text-xl font-bold text-gray-800 mb-4 flex items-center">
        <Lightbulb className="w-5 h-5 mr-2 text-orange-500" />
        What concept do you want to master today?
      </h2>
      
      <form onSubmit={handleSubmit} className="flex-grow flex flex-col space-y-4">
        <textarea
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Describe a topic (Tamil, English, or Tanglish)..."
          className="flex-grow w-full p-4 rounded-xl border border-gray-200 focus:ring-2 focus:ring-[#0f766e] focus:border-transparent resize-none text-lg"
          disabled={isLoading}
        />
        
        <div className="space-y-3">
          <p className="text-sm font-medium text-gray-500 uppercase tracking-wider">Try a demo</p>
          <div className="flex flex-wrap gap-2">
            {demos.map((demo) => (
              <button
                key={demo}
                type="button"
                onClick={() => setInput(demo)}
                disabled={isLoading}
                className="px-3 py-1.5 rounded-lg bg-gray-50 text-gray-700 text-sm hover:bg-teal-50 hover:text-[#0f766e] transition-colors border border-gray-100"
              >
                {demo}
              </button>
            ))}
          </div>
        </div>

        <button
          type="submit"
          disabled={isLoading || !input.trim()}
          className="w-full bg-[#0f766e] text-white py-4 rounded-xl font-bold text-lg flex items-center justify-center space-x-2 hover:bg-[#0d5e58] transition-all disabled:opacity-50 disabled:cursor-not-allowed shadow-lg shadow-teal-900/10 active:scale-[0.98]"
        >
          {isLoading ? (
            <div className="w-6 h-6 border-3 border-white/30 border-t-white rounded-full animate-spin" />
          ) : (
            <>
              <Send className="w-5 h-5" />
              <span>Transform Concept</span>
            </>
          )}
        </button>
      </form>
    </div>
  );
}
