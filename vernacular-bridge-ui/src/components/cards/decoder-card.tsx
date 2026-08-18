import React from 'react';
import { ArrowRight } from 'lucide-react';

interface DecoderCardProps {
  decoder?: {
    question_type: string;
    expected_structure: string;
    answer_template: string;
  };
}

export default function DecoderCard({ decoder }: DecoderCardProps) {
  if (!decoder) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm font-sans mb-6 h-full flex flex-col">
      
      {/* Header */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-6 h-6 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-bold">
          4
        </div>
        <h2 className="text-sm font-bold text-purple-800">Question Decoder</h2>
      </div>

      <div className="bg-[#faf5ff] rounded-xl border border-[#f3e8ff] p-5 flex flex-col md:flex-row items-center justify-between flex-grow">
        
        {/* Left Side */}
        <div className="flex-1 w-full text-left space-y-2">
          <h4 className="text-xs font-bold text-purple-700">If the exam asks...</h4>
          <p className="text-xs text-slate-700 font-medium leading-relaxed">
            Explain the concept of {decoder.question_type}?
          </p>
        </div>

        {/* Arrow */}
        <div className="px-4 py-4 md:py-0">
          <div className="w-6 h-6 rounded-full bg-purple-100 flex items-center justify-center">
            <ArrowRight className="w-3.5 h-3.5 text-purple-600" />
          </div>
        </div>

        {/* Right Side */}
        <div className="flex-1 w-full text-left space-y-2">
          <h4 className="text-xs font-bold text-purple-700">They are really asking...</h4>
          <p className="text-xs text-slate-700 font-medium leading-relaxed">
            {decoder.expected_structure}
          </p>
        </div>
      </div>
      
    </div>
  );
}
