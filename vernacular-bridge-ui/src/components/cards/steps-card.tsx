import React from 'react';
import { ListOrdered, ArrowRight } from 'lucide-react';
import { motion } from 'framer-motion';

interface StepsCardProps {
  steps?: string[];
}

export default function StepsCard({ steps }: StepsCardProps) {
  if (!steps || steps.length === 0) return null;

  return (
    <div className="bg-white rounded-[2.5rem] border border-gray-100 p-12 shadow-sm space-y-12 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-slate-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50" />
      
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center space-x-4">
          <div className="bg-slate-900/5 p-3 rounded-2xl">
            <ListOrdered className="w-6 h-6 text-slate-700" />
          </div>
          <div>
            <h3 className="text-xl font-black text-gray-900 tracking-tight">Step-by-Step Breakdown</h3>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Procedural Understanding</p>
          </div>
        </div>
        <div className="px-4 py-1.5 bg-slate-50 rounded-full border border-slate-100 text-[10px] font-black text-slate-600 uppercase tracking-widest">
          {steps.length} Logical Stages
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 relative z-10">
        {steps.map((step, index) => (
          <motion.div 
            key={index}
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: index * 0.1 }}
            className="group relative bg-[#fcfaf7] p-8 rounded-[2rem] border border-stone-200/60 hover:border-slate-300 transition-all duration-300 hover:shadow-xl hover:shadow-slate-200/40"
          >
            <div className="flex items-start space-x-6">
              <div className="flex-shrink-0">
                <div className="w-12 h-12 bg-white rounded-2xl shadow-sm border border-stone-100 flex items-center justify-center">
                  <span className="text-xl font-black text-slate-800 opacity-20 group-hover:opacity-100 transition-opacity">
                    {index + 1}
                  </span>
                </div>
              </div>
              <div className="space-y-4">
                <p className="text-[1.05rem] font-bold text-slate-800 leading-relaxed tracking-tight">
                  {step}
                </p>
                <div className="flex items-center space-x-2 text-[10px] font-black text-slate-400 uppercase tracking-[0.2em]">
                   <span>Sequence Logged</span>
                   <ArrowRight className="w-3 h-3 group-hover:translate-x-1 transition-transform" />
                </div>
              </div>
            </div>
            
            {/* Visual connector for sequence */}
            {index < steps.length - 1 && (
              <div className="absolute -bottom-3 left-14 w-px h-6 bg-stone-200 z-0 hidden md:block" />
            )}
          </motion.div>
        ))}
      </div>
    </div>
  );
}
