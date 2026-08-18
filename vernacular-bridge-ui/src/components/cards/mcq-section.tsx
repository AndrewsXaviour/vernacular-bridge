import React, { useState } from 'react';
import { Check, RefreshCcw } from 'lucide-react';
import { useLearning } from '@/context/LearningContext';

interface MCQ {
  question: string;
  options: string[];
  correct_answer: string;
}

interface MCQSectionProps {
  mcqs?: MCQ[];
}

export default function MCQSection({ mcqs }: MCQSectionProps) {
  const { updateMCQResult } = useLearning();
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});

  const handleOptionClick = (mcqIndex: number, option: string, isCorrect: boolean) => {
    if (selectedAnswers[mcqIndex] !== undefined) return; 
    setSelectedAnswers(prev => ({ ...prev, [mcqIndex]: option }));
    updateMCQResult(isCorrect, mcqs?.length);
  };

  if (!mcqs || mcqs.length === 0) return null;

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm font-sans mb-6 h-full flex flex-col">
      
      {/* Header section with number */}
      <div className="flex items-center space-x-3 mb-6">
        <div className="w-6 h-6 rounded-full bg-blue-100 text-blue-600 flex items-center justify-center text-xs font-bold">
          5
        </div>
        <h2 className="text-sm font-bold text-blue-700">Practice Now (MCQs)</h2>
      </div>

      <div className="flex-grow space-y-8">
        {mcqs.map((mcq, mIndex) => {
          const selected = selectedAnswers[mIndex];
          const isCorrect = selected === mcq.correct_answer;

          return (
            <div key={mIndex} className="space-y-4">
              <h4 className="text-xs font-bold text-slate-800">Sample MCQ {mIndex > 0 ? mIndex + 1 : ''}</h4>
              <p className="text-sm text-slate-900 font-semibold mb-4">
                {mIndex + 1}. {mcq.question}
              </p>

              <div className="flex flex-wrap gap-2">
                {mcq.options.map((option, oIndex) => {
                  const isOptionSelected = selected === option;
                  const isThisCorrect = option === mcq.correct_answer;
                  
                  let buttonClass = "flex items-center space-x-2 px-3 py-1.5 rounded-lg border text-xs font-bold transition-all ";
                  
                  if (selected) {
                    if (isOptionSelected) {
                      buttonClass += isCorrect 
                        ? "border-green-300 bg-[#ebfbf3] text-green-700" 
                        : "border-red-300 bg-red-50 text-red-700";
                    } else if (isThisCorrect) {
                      buttonClass += "border-green-300 bg-green-50 text-green-700 opacity-70";
                    } else {
                      buttonClass += "border-slate-200 bg-white text-slate-400 opacity-50 cursor-not-allowed";
                    }
                  } else {
                    buttonClass += "border-slate-200 bg-white text-slate-700 hover:border-blue-400 hover:text-blue-700";
                  }

                  return (
                    <button
                      key={oIndex}
                      onClick={() => handleOptionClick(mIndex, option, isThisCorrect)}
                      disabled={!!selected}
                      className={buttonClass}
                    >
                      <span>{String.fromCharCode(65 + oIndex)}. {option}</span>
                      {isOptionSelected && isCorrect && <Check className="w-3.5 h-3.5 text-green-600 ml-1" />}
                    </button>
                  );
                })}
              </div>
            </div>
          );
        })}
      </div>

      <div className="mt-8 pt-4 border-t border-slate-100 flex items-center">
        <button className="flex items-center space-x-2 text-blue-600 hover:text-blue-700 font-bold text-xs py-1.5 px-3 rounded-lg hover:bg-blue-50 transition-colors">
          <RefreshCcw className="w-3.5 h-3.5" />
          <span>Generate More MCQs</span>
        </button>
      </div>

    </div>
  );
}
