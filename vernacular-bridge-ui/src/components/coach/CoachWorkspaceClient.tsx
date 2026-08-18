"use client";

import React, { useState, useRef } from 'react';
import { useSearchParams } from 'next/navigation';
import { PenTool, Target } from 'lucide-react';
import { fetchCoach } from '@/lib/api/coach';
import CoachTextArea from '@/components/coach/CoachTextArea';
import ScoreCard from '@/components/coach/ScoreCard';
import ImprovedAnswer from '@/components/coach/ImprovedAnswer';
import { motion, AnimatePresence } from 'framer-motion';

export default function CoachWorkspaceClient() {
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q') || '';

  const [question, setQuestion] = useState(initialQuery);
  const [studentAnswer, setStudentAnswer] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [feedbackData, setFeedbackData] = useState<any | null>(null);

  const abortControllerRef = useRef<AbortController | null>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  const handleSubmit = async () => {
    if (studentAnswer.trim().length < 5) return;

    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    const controller = new AbortController();
    abortControllerRef.current = controller;

    setIsLoading(true);
    setError(null);
    setFeedbackData(null);

    const promptQuestion = question.length < 5 ? `Explain this concept clearly` : question;

    try {
      const res = await fetchCoach(promptQuestion, studentAnswer, controller.signal);
      setFeedbackData(res);
      setIsLoading(false);
      
      setTimeout(() => {
        resultsRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' });
      }, 100);
    } catch (err: any) {
      if (err.name === 'AbortError') return;
      setError(err.message || 'Failed to analyze answer');
      setIsLoading(false);
    }
  };

  return (
    <div className="relative w-full max-w-5xl mx-auto font-sans pb-12">
      {/* Header */}
      <div className="mb-8 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 flex items-center gap-3">
            <div className="p-2 bg-purple-100 text-purple-600 rounded-xl">
              <PenTool className="w-6 h-6" />
            </div>
            Writing Coach
          </h1>
          <p className="text-sm text-slate-500 mt-2">Draft your answer and receive real-time pedagogical feedback and rigor scoring.</p>
        </div>
      </div>

      <div className="space-y-6">
        {/* Context Input */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <label className="block text-sm font-bold uppercase tracking-wider text-slate-500 mb-3 flex items-center gap-2">
            <Target className="w-4 h-4 text-slate-400" />
            What concept or question are you answering?
          </label>
          <input
            type="text"
            value={question}
            onChange={(e) => setQuestion(e.target.value)}
            placeholder="e.g. Explain the process of Photosynthesis"
            className="w-full px-4 py-3 bg-slate-50 border border-slate-200 rounded-xl focus:ring-2 focus:ring-purple-500/20 focus:border-purple-300 transition-all outline-none text-slate-700 font-medium"
          />
        </div>

        {/* Text Area */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <CoachTextArea
            value={studentAnswer}
            onChange={setStudentAnswer}
            onSubmit={handleSubmit}
            loading={isLoading}
          />
        </div>

        {/* Error State */}
        {error && (
          <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-medium animate-in fade-in">
            {error}
          </div>
        )}

        {/* Results Area */}
        <div ref={resultsRef} className="scroll-mt-24">
          <AnimatePresence mode="wait">
            {feedbackData && (
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                className="space-y-6 mt-8"
              >
                <div className="flex items-center gap-3 mb-2">
                  <div className="h-px bg-slate-200 flex-1" />
                  <span className="text-xs font-bold text-slate-400 uppercase tracking-widest">Analysis Results</span>
                  <div className="h-px bg-slate-200 flex-1" />
                </div>

                <ScoreCard
                  score={feedbackData.score}
                  strengths={feedbackData.strengths}
                  weaknesses={feedbackData.weaknesses}
                  missing_points={feedbackData.missing_points}
                  improvement_suggestions={feedbackData.improvement_suggestions}
                />
                <ImprovedAnswer content={feedbackData.improved_answer} />
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </div>
    </div>
  );
}
