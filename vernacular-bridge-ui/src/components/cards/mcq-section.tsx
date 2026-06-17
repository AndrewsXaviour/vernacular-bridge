import React, { useState } from 'react';
import { HelpCircle, CheckCircle, XCircle, Lightbulb, RefreshCw } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
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
  const { updateMCQResult, goToStage } = useLearning();
  const [selectedAnswers, setSelectedAnswers] = useState<Record<number, string>>({});

  const handleOptionClick = (mcqIndex: number, option: string, isCorrect: boolean) => {
    if (selectedAnswers[mcqIndex] !== undefined) return; 
    setSelectedAnswers(prev => ({ ...prev, [mcqIndex]: option }));
    updateMCQResult(isCorrect, mcqs?.length);
  };

  if (!mcqs || mcqs.length === 0) return null;

  return (
    <div className="bg-white rounded-[2.5rem] border border-gray-100 p-10 shadow-sm space-y-12">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-3">
          <div className="bg-amber-500/10 p-2.5 rounded-xl">
            <HelpCircle className="w-5 h-5 text-amber-600" />
          </div>
          <div>
            <h3 className="text-lg font-black text-gray-900 tracking-tight">Intelligence Check</h3>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Validating Concept Acquisition</p>
          </div>
        </div>
        <div className="px-4 py-1.5 bg-amber-50 rounded-full border border-amber-100 text-[10px] font-black text-amber-700 uppercase tracking-widest">
          {Object.keys(selectedAnswers).length} / {mcqs.length} COMPLETED
        </div>
      </div>

      <div className="space-y-16">
        {mcqs.map((mcq, mIndex) => {
          const selected = selectedAnswers[mIndex];
          const isCorrect = selected === mcq.correct_answer;

          return (
            <div key={mIndex} className="space-y-8 relative">
              {mIndex > 0 && <div className="absolute -top-8 left-0 right-0 h-px bg-gray-50" />}
              
              <div className="space-y-4">
                <div className="flex items-center space-x-3">
                  <span className="text-[10px] font-black bg-gray-900 text-white px-2.5 py-1 rounded-lg uppercase tracking-widest">Question {mIndex + 1}</span>
                </div>
                <h4 className="text-xl font-bold text-gray-900 leading-tight">
                  {mcq.question}
                </h4>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {mcq.options.map((option, oIndex) => {
                  const isOptionSelected = selected === option;
                  const isThisCorrect = option === mcq.correct_answer;
                  
                  let buttonClass = "group p-6 rounded-2xl border-2 border-gray-100 text-left transition-all duration-300 hover:border-teal-200 hover:bg-teal-50/30";
                  
                  if (selected) {
                    if (isOptionSelected) {
                      buttonClass = isCorrect 
                        ? "p-6 rounded-2xl border-2 border-[#0f766e] bg-teal-50 text-[#0f766e] shadow-lg shadow-teal-900/5 scale-[1.02]" 
                        : "p-6 rounded-2xl border-2 border-red-500 bg-red-50 text-red-900 opacity-90";
                    } else if (isThisCorrect) {
                       buttonClass = "p-6 rounded-2xl border-2 border-green-100 bg-green-50/20 text-green-800 opacity-50";
                    } else {
                       buttonClass = "p-6 rounded-2xl border border-gray-100 text-gray-300 opacity-30 cursor-not-allowed";
                    }
                  }

                  return (
                    <button
                      key={oIndex}
                      onClick={() => handleOptionClick(mIndex, option, isThisCorrect)}
                      disabled={!!selected}
                      className={buttonClass}
                    >
                      <div className="flex items-center space-x-4">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-xs font-black transition-colors
                          ${isOptionSelected && isCorrect ? 'bg-[#0f766e] text-white' : 
                            isOptionSelected && !isCorrect ? 'bg-red-500 text-white' : 
                            'bg-gray-100 text-gray-400 group-hover:bg-teal-100 group-hover:text-teal-600'}
                        `}>
                          {String.fromCharCode(65 + oIndex)}
                        </div>
                        <span className="flex-grow font-bold text-[0.95rem]">{option}</span>
                        {isOptionSelected && (
                          isCorrect ? <CheckCircle className="w-5 h-5 text-[#0f766e]" /> : <XCircle className="w-5 h-5 text-red-600" />
                        )}
                      </div>
                    </button>
                  );
                })}
              </div>

              <AnimatePresence>
                {selected && (
                  <motion.div 
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    className={`p-6 rounded-2xl border ${isCorrect ? 'bg-teal-50 border-teal-100' : 'bg-amber-50 border-amber-100'} space-y-4`}
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                         <Lightbulb className={`w-4 h-4 ${isCorrect ? 'text-[#0f766e]' : 'text-amber-600'}`} />
                         <span className={`text-[10px] font-black uppercase tracking-widest ${isCorrect ? 'text-[#0f766e]' : 'text-amber-700'}`}>
                           {isCorrect ? 'Verification Success' : 'Common Misconception Alert'}
                         </span>
                      </div>
                      {!isCorrect && (
                        <button 
                          onClick={() => goToStage('steps')}
                          className="flex items-center space-x-2 bg-white px-3 py-1 rounded-lg border border-amber-200 text-[10px] font-black text-amber-700 uppercase tracking-widest hover:bg-amber-100 transition-colors shadow-sm"
                        >
                          <RefreshCw className="w-3 h-3" />
                          <span>Review Related Step</span>
                        </button>
                      )}
                    </div>
                    <p className={`text-sm font-bold leading-relaxed ${isCorrect ? 'text-[#0f766e]' : 'text-amber-800'}`}>
                      {isCorrect 
                        ? "Spot on! This indicates a deep understanding of the core mechanism. Your mastery score has been updated."
                        : `Wait! Common mistake here. The correct answer is "${mcq.correct_answer}". Focus on the relationship between energy input and the resulting synthesis.`
                      }
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          );
        })}
      </div>
    </div>
  );
}
