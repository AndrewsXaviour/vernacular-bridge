import React from 'react';
import { Target, Layout, FileText, ChevronRight } from 'lucide-react';
import { motion } from 'framer-motion';

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
    <div className="bg-white rounded-[2.5rem] border border-gray-100 p-12 shadow-sm space-y-12 relative overflow-hidden">
      <div className="absolute top-0 right-0 w-64 h-64 bg-violet-50 rounded-full -mr-32 -mt-32 blur-3xl opacity-50" />
      
      <div className="flex items-center justify-between relative z-10">
        <div className="flex items-center space-x-4">
          <div className="bg-violet-600/10 p-3 rounded-2xl">
            <Target className="w-6 h-6 text-violet-600" />
          </div>
          <div>
            <h3 className="text-xl font-black text-gray-900 tracking-tight">Exam Intelligence Decoder</h3>
            <p className="text-[10px] text-gray-400 font-bold uppercase tracking-widest">Strategic Assessment Mapping</p>
          </div>
        </div>
        <div className="px-5 py-2 bg-violet-50 rounded-full border border-violet-100 text-[10px] font-black text-violet-700 uppercase tracking-widest shadow-sm">
          Scoring Optimization Active
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-8 relative z-10">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="group space-y-5"
        >
          <div className="flex items-center space-x-3 text-violet-600 text-[10px] font-black uppercase tracking-[0.2em] mb-1">
            <div className="w-1.5 h-1.5 bg-violet-600 rounded-full" />
            <span>Target Question Type</span>
          </div>
          <div className="p-8 bg-violet-50/30 rounded-[2rem] border border-violet-100/50 text-violet-900 font-black text-xl capitalize shadow-sm group-hover:bg-violet-50 transition-colors">
            {decoder.question_type}
          </div>
          <p className="text-[10px] text-gray-400 font-bold leading-relaxed px-2">
            Optimized for maximum mark extraction based on linguistic cues.
          </p>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="group space-y-5"
        >
          <div className="flex items-center space-x-3 text-indigo-600 text-[10px] font-black uppercase tracking-[0.2em] mb-1">
            <div className="w-1.5 h-1.5 bg-indigo-600 rounded-full" />
            <span>Success Structure</span>
          </div>
          <div className="p-8 bg-indigo-50/30 rounded-[2rem] border border-indigo-100/50 text-indigo-900 text-[0.95rem] leading-relaxed font-bold group-hover:bg-indigo-50 transition-colors h-full">
            {decoder.expected_structure}
          </div>
        </motion.div>

        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
          className="group space-y-5"
        >
          <div className="flex items-center space-x-3 text-teal-600 text-[10px] font-black uppercase tracking-[0.2em] mb-1">
            <div className="w-1.5 h-1.5 bg-teal-600 rounded-full" />
            <span>Response Engine Template</span>
          </div>
          <div className="p-8 bg-teal-50/20 rounded-[2rem] border-2 border-dashed border-teal-200 text-[#0f766e] leading-relaxed font-mono text-sm italic group-hover:bg-teal-50/40 transition-colors relative">
             <FileText className="absolute top-4 right-4 w-4 h-4 opacity-20" />
             "{decoder.answer_template}"
          </div>
        </motion.div>
      </div>

      <div className="pt-10 border-t border-gray-50 flex items-center justify-center space-x-12 relative z-10">
         <div className="flex items-center space-x-4 group cursor-pointer">
           <div className="text-[10px] font-black text-gray-400 uppercase tracking-widest group-hover:text-violet-600 transition-colors">View Evaluation Rubric</div>
           <ChevronRight className="w-4 h-4 text-gray-400 group-hover:translate-x-1 transition-all" />
         </div>
      </div>
    </div>
  );
}
