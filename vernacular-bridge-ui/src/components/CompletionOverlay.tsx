'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Trophy, ArrowRight, RefreshCw, Star, BarChart } from 'lucide-react';

interface CompletionOverlayProps {
  isVisible: boolean;
  mastery: number;
  accuracy: number;
  timeSpent: number;
  onReset: () => void;
}

export default function CompletionOverlay({ isVisible, mastery, accuracy, timeSpent, onReset }: CompletionOverlayProps) {
  if (!isVisible) return null;

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div 
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          className="fixed inset-0 z-[200] flex items-center justify-center p-6 bg-slate-900/40 backdrop-blur-md"
        >
          <motion.div 
            initial={{ scale: 0.9, opacity: 0, y: 20 }}
            animate={{ scale: 1, opacity: 1, y: 0 }}
            className="bg-white rounded-[3rem] shadow-2xl max-w-2xl w-full p-12 text-center space-y-10 relative overflow-hidden"
          >
            {/* Decorative background Elements */}
            <div className="absolute top-0 left-0 w-full h-2 bg-gradient-to-r from-teal-500 via-indigo-500 to-amber-500" />
            <div className="absolute -top-24 -right-24 w-64 h-64 bg-teal-50 rounded-full blur-3xl opacity-60" />
            <div className="absolute -bottom-24 -left-24 w-64 h-64 bg-indigo-50 rounded-full blur-3xl opacity-60" />

            <div className="space-y-4 relative z-10">
              <div className="inline-flex p-4 rounded-3xl bg-teal-50 text-teal-600 mb-4 shadow-sm border border-teal-100/50">
                <Trophy className="w-12 h-12" />
              </div>
              <h2 className="text-4xl font-black text-slate-900 tracking-tight">Concept Mastered!</h2>
              <p className="text-slate-500 font-bold uppercase tracking-widest text-xs px-12 leading-relaxed">
                You have successfully converted vernacular understanding into academic excellence.
              </p>
            </div>

            <div className="grid grid-cols-3 gap-6 relative z-10">
              <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100 flex flex-col items-center space-y-2">
                <div className="p-2 rounded-xl bg-teal-500/10 text-teal-600">
                  <Star className="w-5 h-5 fill-teal-600" />
                </div>
                <div className="text-2xl font-black text-slate-900">{mastery}%</div>
                <div className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Overall Mastery</div>
              </div>

              <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100 flex flex-col items-center space-y-2">
                <div className="p-2 rounded-xl bg-indigo-500/10 text-indigo-600">
                  <BarChart className="w-5 h-5 fill-indigo-600" />
                </div>
                <div className="text-2xl font-black text-slate-900">{accuracy}%</div>
                <div className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Accuracy Rate</div>
              </div>

              <div className="bg-slate-50 p-6 rounded-[2rem] border border-slate-100 flex flex-col items-center space-y-2">
                <div className="p-2 rounded-xl bg-amber-500/10 text-amber-600">
                  <RefreshCw className="w-5 h-5" />
                </div>
                <div className="text-2xl font-black text-slate-900">{formatTime(timeSpent)}</div>
                <div className="text-[10px] font-black text-slate-400 uppercase tracking-tighter">Session Time</div>
              </div>
            </div>

            <div className="flex flex-col space-y-4 relative z-10">
              <button 
                onClick={onReset}
                className="w-full bg-[#0f766e] text-white py-5 rounded-[1.5rem] font-black text-lg shadow-xl shadow-teal-900/20 hover:bg-[#0d635c] transition-all transform hover:-translate-y-1 active:translate-y-0 flex items-center justify-center space-x-3 group"
              >
                <span>Master Next Concept</span>
                <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
              </button>
              
              <button 
                onClick={onReset}
                className="w-full bg-white text-slate-400 py-4 rounded-[1.5rem] font-bold text-sm hover:text-slate-600 transition-colors"
              >
                Return to Dashboard
              </button>
            </div>

            <div className="pt-4 opacity-30 relative z-10">
               <div className="text-[10px] font-black text-slate-400 uppercase tracking-[0.3em]">Vernacular Bridge Engine 2.0</div>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
