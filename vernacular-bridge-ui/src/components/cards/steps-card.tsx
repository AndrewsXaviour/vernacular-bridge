import React from 'react';
import { Sun, Droplet, FlaskConical, Package, ArrowRight } from 'lucide-react';

interface StepsCardProps {
  steps?: string[];
}

export default function StepsCard({ steps }: StepsCardProps) {
  if (!steps || steps.length === 0) return null;

  const icons = [
    <div key="sun" className="w-12 h-12 rounded-full bg-green-50 flex items-center justify-center text-green-600"><Sun className="w-6 h-6" /></div>,
    <div key="droplet" className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-500"><Droplet className="w-6 h-6" /></div>,
    <div key="flask" className="w-12 h-12 rounded-full bg-emerald-50 flex items-center justify-center text-emerald-600"><FlaskConical className="w-6 h-6" /></div>,
    <div key="package" className="w-12 h-12 rounded-full bg-blue-50 flex items-center justify-center text-blue-600"><Package className="w-6 h-6" /></div>,
  ];

  return (
    <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm font-sans mb-6">
      
      {/* Header section with number */}
      <div className="flex items-center space-x-3 mb-8">
        <div className="w-6 h-6 rounded-full bg-purple-100 text-purple-700 flex items-center justify-center text-xs font-bold">
          3
        </div>
        <h2 className="text-sm font-bold text-purple-800">How it Works (Steps)</h2>
      </div>

      <div className="flex items-start justify-between relative px-2">
        {steps.map((step, index) => {
          // Split title and description if format is "Title: Description"
          const parts = step.split(':');
          const title = parts.length > 1 ? parts[0].trim() : `Step ${index + 1}`;
          const description = parts.length > 1 ? parts.slice(1).join(':').trim() : step;

          return (
            <React.Fragment key={index}>
              <div className="flex flex-col items-center flex-1 max-w-[200px] text-center z-10">
                <div className="mb-4">
                  {icons[index % icons.length]}
                </div>
                <h4 className="text-xs font-bold text-slate-800 mb-1">
                  {index + 1}. {title}
                </h4>
                <p className="text-[11px] text-slate-500 font-medium leading-relaxed">
                  {description}
                </p>
              </div>

              {index < steps.length - 1 && (
                <div className="hidden md:flex flex-1 items-center justify-center mt-6 z-0">
                  <ArrowRight className="w-4 h-4 text-blue-600" />
                </div>
              )}
            </React.Fragment>
          );
        })}
      </div>
      
    </div>
  );
}
