"use client";

import React, { useState, useEffect, useRef } from 'react';
import InputPanel from '@/components/input-panel';
import TransformationStepper from '@/components/transformation-stepper';
import TamilCard from '@/components/cards/tamil-card';
import EnglishCard from '@/components/cards/academic-card';
import StepsCard from '@/components/cards/steps-card';
import DecoderCard from '@/components/cards/decoder-card';
import MCQSection from '@/components/cards/mcq-section';
import { motion, AnimatePresence } from 'framer-motion';
import { LearningProvider, useLearning } from '@/context/LearningContext';
import { PlayCircle, Clock } from 'lucide-react';
import { useSearchParams } from 'next/navigation';

function LearnWorkspaceContent() {
  const { state, updateStage, completeStage, incrementTime, isResuming, resetForNewConcept } = useLearning();
  const { currentStage: activeTab, mastery, isCompleted, accuracy, timeSpent, conceptId, completedStages } = state;
  
  const searchParams = useSearchParams();
  const initialQuery = searchParams.get('q');
  
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [loadingText, setLoadingText] = useState("");
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [demoMode, setDemoMode] = useState(false);
  const hasTriggeredInitialQuery = useRef(false);

  const lastMastery = useRef(mastery);
  const [showMasteryToast, setShowMasteryToast] = useState(false);
  const endOfContentRef = useRef<HTMLDivElement>(null);

  const handleTransform = async (text: string) => {
    // Generate a simple Unicode-safe hash for concept identification
    const encodedText = Array.from(new TextEncoder().encode(text.slice(0, 10)), (b) => String.fromCharCode(b)).join('');
    const newConceptId = btoa(encodedText).replace(/[^a-zA-Z0-9]/g, '') || `concept_${Date.now()}`;
    resetForNewConcept(newConceptId);
    
    setIsLoading(true);
    setError(null);
    setShowResults(true);
    setData(null);
    setCurrentStage(0);

    try {
      const progressStages = [
        { text: "Analyzing semantic context...", stage: 1 },
        { text: "Mapping vernacular logic...", stage: 2 },
        { text: "Cross-bridging academic terms...", stage: 3 },
        { text: "Synthesizing exam metrics...", stage: 4 },
      ];

      if (!demoMode) {
        for (const step of progressStages) {
          setLoadingText(step.text);
          await new Promise(r => setTimeout(r, 800));
          setCurrentStage(step.stage);
        }
      }

      // Fetch with AbortController timeout and exponential backoff retry
      const MAX_RETRIES = 3;
      const TIMEOUT_MS = 30000;
      let lastError: Error | null = null;

      for (let attempt = 0; attempt <= MAX_RETRIES; attempt++) {
        try {
          const controller = new AbortController();
          const timeoutId = setTimeout(() => controller.abort(), TIMEOUT_MS);

          const response = await fetch("/api/generate", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ user_input: text }),
            signal: controller.signal,
          });
          clearTimeout(timeoutId);

          if (!response.ok) throw new Error("Connection failed with intelligence bridge");
          const rawData = await response.json();
          if (rawData.status === "error") throw new Error(rawData.message || "Logic synthesis failed");

          setData({
            tamil_simple: rawData?.tamil_simple ?? "",
            english_academic: rawData?.english_academic ?? "",
            steps: Array.isArray(rawData?.steps) ? rawData.steps : [],
            question_decoder: {
              question_type: rawData?.question_decoder?.question_type ?? "explain",
              expected_structure: rawData?.question_decoder?.expected_structure ?? "",
              answer_template: rawData?.question_decoder?.answer_template ?? ""
            },
            mcqs: Array.isArray(rawData?.mcqs) ? rawData.mcqs : []
          });
          setIsLoading(false);
          return; // success, exit retry loop
        } catch (err: any) {
          lastError = err;
          if (err.name === "AbortError") {
            lastError = new Error("Connection timeout — backend may be down");
          }
          if (attempt < MAX_RETRIES) {
            const delay = Math.min(1000 * Math.pow(2, attempt), 8000);
            await new Promise(r => setTimeout(r, delay));
          }
        }
      }
      // All retries exhausted
      throw lastError || new Error("Request failed after retries");
    } catch (err: any) {
      console.error("Engine failure:", err);
      setError(err.message || "An unexpected logic error occurred");
      setIsLoading(false);
    }
  };

  // Auto-trigger if there's a query param
  useEffect(() => {
    if (initialQuery && !hasTriggeredInitialQuery.current) {
      hasTriggeredInitialQuery.current = true;
      handleTransform(initialQuery);
    }
  }, [initialQuery]);

  // Auto-scroll to newly unlocked content
  useEffect(() => {
    if (endOfContentRef.current && showResults && !isLoading) {
      setTimeout(() => {
        endOfContentRef.current?.scrollIntoView({ behavior: 'smooth', block: 'end' });
      }, 100);
    }
  }, [activeTab, showResults, isLoading]);

  // Time Tracking
  useEffect(() => {
    let timer: NodeJS.Timeout;
    if (showResults && !isCompleted) {
      timer = setInterval(incrementTime, 1000);
    }
    return () => clearInterval(timer);
  }, [showResults, isCompleted, incrementTime]);

  return (
    <div className="relative w-full max-w-5xl mx-auto font-sans">
      
      {/* Header */}
      <div className="mb-6 flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">Concept Bridge (Learn)</h1>
          <p className="text-sm text-slate-500 mt-1">Understand any concept in Tamil and bridge it to Academic English.</p>
        </div>
        <div className="flex items-center space-x-3">
          <button className="flex items-center space-x-2 px-3 py-1.5 border border-slate-200 rounded-lg text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors">
            <PlayCircle className="w-4 h-4 text-slate-500" />
            <span>How it works</span>
          </button>
          <button className="flex items-center space-x-2 px-3 py-1.5 border border-slate-200 rounded-lg text-sm font-bold text-slate-700 hover:bg-slate-50 transition-colors">
            <Clock className="w-4 h-4 text-slate-500" />
            <span>History</span>
          </button>
        </div>
      </div>

      {/* Input Panel Always visible */}
      <InputPanel 
        onTransform={handleTransform} 
        isLoading={isLoading} 
        demoMode={demoMode} 
        initialValue={initialQuery || ""}
      />

      {/* Loading Experience */}
      {isLoading && (
        <div className="bg-white p-12 rounded-2xl shadow-sm border border-slate-200 flex flex-col items-center mt-6">
          <TransformationStepper currentStage={currentStage} />
          <div className="mt-12 flex flex-col items-center space-y-6">
            <div className="relative">
              <div className="w-16 h-16 border-[4px] border-blue-600/10 border-t-blue-600 rounded-full animate-spin" />
              <div className="absolute inset-0 flex items-center justify-center">
                <div className="w-2 h-2 bg-blue-600 rounded-full animate-ping" />
              </div>
            </div>
            <div className="flex flex-col items-center space-y-1">
              <span className="text-sm font-bold text-slate-700">Connecting vernacular to academic framework</span>
              <span className="text-xs text-slate-500 font-medium">{loadingText}</span>
            </div>
          </div>
        </div>
      )}

      {/* Results Area */}
      {showResults && !isLoading && !error && data && (
        <div className="flex flex-col w-full mt-6 space-y-6">
          
          {/* Bilingual Core */}
          {(activeTab === 'tamil' || completedStages.includes('tamil')) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onAnimationComplete={() => completeStage('tamil')}
              className="w-full relative"
            >
              <div className="flex items-center space-x-3 mb-6">
                <div className="w-6 h-6 rounded-full bg-green-100 text-green-700 flex items-center justify-center text-xs font-bold">
                  2
                </div>
                <h2 className="text-sm font-bold text-green-800">Bilingual Explanation</h2>
              </div>

              <div className={`grid grid-cols-1 gap-6 w-full ${(activeTab === 'english' || completedStages.includes('english') || completedStages.includes('tamil')) && activeTab !== 'tamil' ? 'lg:grid-cols-2' : ''}`}>
                <TamilCard content={data.tamil_simple} />
                {(activeTab === 'english' || completedStages.includes('english')) && (
                  <motion.div
                     initial={{ opacity: 0, x: -20 }}
                     animate={{ opacity: 1, x: 0 }}
                     onAnimationComplete={() => completeStage('english')}
                     className="h-full"
                  >
                    <EnglishCard content={data.english_academic} />
                  </motion.div>
                )}
              </div>
            </motion.div>
          )}

          {/* Steps */}
          {(activeTab === 'steps' || completedStages.includes('steps')) && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              onAnimationComplete={() => completeStage('steps')}
              className="w-full"
            >
              <StepsCard steps={data.steps} />
            </motion.div>
          )}

          {/* Decoder and MCQ Side-by-Side */}
          {((activeTab === 'exam' || completedStages.includes('exam')) || (activeTab === 'mcq' || completedStages.includes('mcq'))) && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 w-full items-stretch">
              {/* Decoder */}
              {(activeTab === 'exam' || completedStages.includes('exam')) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  onAnimationComplete={() => completeStage('exam')}
                  className="w-full h-full"
                >
                  <DecoderCard decoder={data.question_decoder} />
                </motion.div>
              )}

              {/* MCQs */}
              {(activeTab === 'mcq' || completedStages.includes('mcq')) && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  onAnimationComplete={() => completeStage('mcq')}
                  className="w-full h-full"
                >
                  <MCQSection mcqs={data.mcqs} />
                </motion.div>
              )}
            </div>
          )}

          {/* Progressive Unlock Action */}
          {activeTab !== 'mcq' && (
            <div className="flex justify-end pt-4 pb-12 w-full">
               <button 
                 onClick={() => {
                   const tabs = ['tamil', 'english', 'steps', 'exam', 'mcq'];
                   const nextTab = tabs[tabs.indexOf(activeTab) + 1];
                   updateStage(nextTab as any);
                 }}
                 className="bg-slate-900 text-white px-6 py-2.5 rounded-lg font-bold text-sm shadow-sm hover:bg-slate-800 transition-colors"
               >
                 Unlock Next Module
               </button>
            </div>
          )}
          
          {/* Scroll Target */}
          <div ref={endOfContentRef} className="h-4" />
        </div>
      )}
    </div>
  );
}

export default function LearnPage() {
  return (
    <LearningProvider initialConceptId="default">
      <React.Suspense fallback={<div className="p-8 text-center text-slate-500">Loading workspace...</div>}>
        <LearnWorkspaceContent />
      </React.Suspense>
    </LearningProvider>
  );
}
