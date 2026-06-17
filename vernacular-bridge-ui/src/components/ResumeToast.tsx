'use client';

import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { RefreshCw } from 'lucide-react';

interface ResumeToastProps {
  isVisible: boolean;
}

export default function ResumeToast({ isVisible }: ResumeToastProps) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 50, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, scale: 1 }}
          exit={{ opacity: 0, y: 20, scale: 0.9 }}
          className="fixed bottom-8 right-8 z-[100] flex items-center space-x-3 bg-[#0f766e] text-white px-6 py-4 rounded-2xl shadow-2xl border border-white/10"
        >
          <div className="bg-white/20 p-1.5 rounded-lg animate-spin-slow">
            <RefreshCw className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-bold tracking-tight">Syncing Journey</span>
            <span className="text-[10px] opacity-70 font-medium uppercase tracking-widest">Resuming your progress...</span>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
