import React from 'react';
import { Check } from 'lucide-react';

interface TransformationStepperProps {
  currentStage: number; // 0: Input, 1: Tamil, 2: English, 3: Exam, 4: Assessment
}

const stages = [
  "Understanding",
  "Upgrading",
  "Intelligence",
  "Assignment"
];

export default function TransformationStepper({ currentStage }: TransformationStepperProps) {
  return (
    <div className="w-full py-6">
      <div className="flex items-center justify-between">
        {stages.map((stage, index) => {
          const stepNumber = index + 1;
          const isActive = stepNumber <= currentStage;
          const isCompleted = stepNumber < currentStage;

          return (
            <React.Fragment key={stage}>
              {/* Step */}
              <div className="flex flex-col items-center relative flex-1">
                <div 
                  className={`w-10 h-10 rounded-full flex items-center justify-center border-2 transition-all duration-500 z-10 ${
                    isActive 
                      ? 'bg-[#0f766e] border-[#0f766e] text-white' 
                      : 'bg-white border-gray-200 text-gray-300'
                  }`}
                >
                  {isCompleted ? (
                    <Check className="w-6 h-6" />
                  ) : (
                    <span className="font-bold">{stepNumber}</span>
                  )}
                </div>
                <span 
                  className={`mt-2 text-xs font-bold uppercase tracking-tight text-center transition-colors duration-500 ${
                    isActive ? 'text-[#0f766e]' : 'text-gray-400'
                  }`}
                >
                  {stage}
                </span>
                
                {/* Connector line (except for last) */}
                {index < stages.length - 1 && (
                  <div 
                    className={`absolute top-5 left-[calc(50%+1.25rem)] w-[calc(100%-2.5rem)] h-[2px] transition-colors duration-500 -z-0 ${
                      isCompleted ? 'bg-[#0f766e]' : 'bg-gray-200'
                    }`}
                  />
                )}
              </div>
            </React.Fragment>
          );
        })}
      </div>
    </div>
  );
}
