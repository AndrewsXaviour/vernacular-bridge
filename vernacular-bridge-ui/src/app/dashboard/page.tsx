'use client';

import React, { useState, useEffect, useRef } from 'react';
import Navbar from '@/components/navbar';
import InputPanel from '@/components/input-panel';
import ResultPlaceholder from '@/components/result-placeholder';
import TransformationStepper from '@/components/transformation-stepper';
import TamilCard from '@/components/cards/tamil-card';
import EnglishCard from '@/components/cards/academic-card';
import StepsCard from '@/components/cards/steps-card';
import DecoderCard from '@/components/cards/decoder-card';
import MCQSection from '@/components/cards/mcq-section';
import DashboardSidebar from '@/components/dashboard-sidebar';
import ResumeToast from '@/components/ResumeToast';
import CompletionOverlay from '@/components/CompletionOverlay';
import { motion, AnimatePresence } from 'framer-motion';
import { LearningProvider, useLearning } from '@/context/LearningContext';
import { Trophy, Star } from 'lucide-react';

function DashboardContent({ showResults, setShowResults, isLoading, handleTransform, error, data, loadingText, currentStage, demoMode, setDemoMode }: any) {
  const { state, updateStage, completeStage, incrementTime, isResuming, resetForNewConcept } = useLearning();
  const { currentStage: activeTab, mastery, isCompleted, accuracy, timeSpent, conceptId } = state;
  const lastMastery = useRef(mastery);
  const [showMasteryToast, setShowMasteryToast] = useState(false);

  // Time Tracking
  useEffect(() => {
    if (showResults && !isLoading && !error && !isCompleted) {
      const timer = setInterval(() => incrementTime(), 1000);
      return () => clearInterval(timer);
    }
  }, [showResults, isLoading, error, incrementTime, isCompleted]);

  // Mastery Feedback
  useEffect(() => {
    if (mastery > lastMastery.current) {
      setShowMasteryToast(true);
      setTimeout(() => setShowMasteryToast(false), 3000);
    }
    lastMastery.current = mastery;
  }, [mastery]);

  const handleFinishNext = () => {
    setShowResults(false);
    resetForNewConcept('default');
  };

  return (
    <div className="flex-grow flex overflow-hidden relative font-outfit">
      <ResumeToast isVisible={isResuming} />
      
      <CompletionOverlay 
        isVisible={isCompleted} 
        mastery={mastery} 
        accuracy={accuracy} 
        timeSpent={timeSpent}
        onReset={handleFinishNext}
      />
      
      {/* Mastery Toast */}
      <AnimatePresence>
        {showMasteryToast && (
          <motion.div 
            initial={{ y: -100, opacity: 0 }}
            animate={{ y: 20, opacity: 1 }}
            exit={{ y: -100, opacity: 0 }}
            className="absolute top-4 left-1/2 -translate-x-1/2 z-[100] bg-white border border-teal-100 px-6 py-3 rounded-2xl shadow-xl flex items-center space-x-3"
          >
            <div className="bg-[#0f766e] p-1.5 rounded-lg shadow-sm">
              <Star className="w-4 h-4 text-white fill-white" />
            </div>
            <span className="text-sm font-black text-teal-900 tracking-tight">+10% Mastery Achieved 🎯</span>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Sidebar - Only shown on results and desktop */}
      <AnimatePresence>
        {showResults && !error && (
          <motion.div 
            initial={{ x: -320, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            exit={{ x: -320, opacity: 0 }}
            transition={{ type: 'spring', damping: 25, stiffness: 200 }}
            className="w-80 h-full hidden lg:block"
          >
            <DashboardSidebar />
          </motion.div>
        )}
      </AnimatePresence>

      {/* Workspace */}
      <div className="flex-grow overflow-y-auto bg-slate-50/30">
        {!showResults ? (
          <div className="max-w-4xl mx-auto w-full p-12 flex flex-col space-y-16 min-h-full py-20">
            <div className="text-center space-y-6">
              <div className="space-y-2">
                <h1 className="text-5xl font-black text-slate-900 tracking-tight">Vernacular Bridge</h1>
                <p className="text-[#0f766e] font-black tracking-[0.2em] uppercase text-[10px] bg-teal-50 inline-block px-5 py-2 rounded-full mx-auto border border-teal-100/50">Intelligence Orchestrator</p>
              </div>
              <p className="text-slate-400 font-bold text-lg max-w-lg mx-auto leading-relaxed">
                Converting native understanding into <span className="text-slate-800 underline decoration-teal-500 decoration-2 underline-offset-4">exam-ready academic knowledge</span>.
              </p>
            </div>
            <InputPanel 
              onTransform={handleTransform} 
              isLoading={isLoading} 
              demoMode={demoMode} 
            />
            <div className="max-w-2xl mx-auto w-full pt-4">
              <ResultPlaceholder />
            </div>
            
            <div className="flex justify-center pt-8">
              <button 
                onClick={() => setDemoMode(!demoMode)}
                className={`text-[10px] font-black uppercase tracking-widest px-4 py-2 rounded-xl transition-all
                  ${demoMode ? 'bg-amber-100 text-amber-700 border border-amber-200' : 'text-slate-300 hover:text-slate-400'}
                `}
              >
                Demo Control Mode: {demoMode ? 'ON' : 'OFF'}
              </button>
            </div>
          </div>
        ) : (
          <div className="p-12 h-full flex flex-col items-center">
            <div className={`w-full ${error ? 'max-w-4xl' : 'max-w-5xl'} space-y-10`}>
              {/* Header Actions */}
              <div className="flex items-center justify-between pb-4 border-b border-slate-100">
                <button 
                  onClick={() => setShowResults(false)}
                  className="text-xs font-bold text-slate-400 hover:text-[#0f766e] flex items-center space-x-2 group transition-colors"
                >
                  <div className="p-1.5 rounded-lg bg-white border border-slate-200 group-hover:border-teal-200 transition-colors shadow-sm">
                    <svg className="w-3.5 h-3.5 group-hover:-translate-x-0.5 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M15 19l-7-7 7-7" />
                    </svg>
                  </div>
                  <span className="uppercase tracking-widest text-[10px]">Back to entry</span>
                </button>
                <div className="flex items-center space-x-4">
                  <div className="px-5 py-2 bg-white border border-slate-100 rounded-full text-[10px] font-black text-slate-500 uppercase tracking-widest shadow-sm flex items-center space-x-2.5">
                    <div className="w-2 h-2 bg-teal-500 rounded-full animate-pulse shadow-[0_0_8px_rgba(20,184,166,0.5)]" />
                    <span>Mapping Process Active</span>
                  </div>
                </div>
              </div>

              {/* Error Box */}
              <AnimatePresence>
                {error && (
                  <motion.div 
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="p-10 bg-[#0f172a] border border-slate-800 rounded-[2.5rem] flex items-center space-x-8 text-white shadow-2xl"
                  >
                    <div className="bg-red-500/20 p-5 rounded-2xl text-red-400 border border-red-500/30">
                      <svg className="w-8 h-8" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                      </svg>
                    </div>
                    <div>
                      <h4 className="text-2xl font-bold mb-2 tracking-tight">System Interrupt</h4>
                      <p className="opacity-60 text-[0.95rem] leading-relaxed max-w-md">{error}</p>
                      <button onClick={() => setShowResults(false)} className="mt-6 px-6 py-2.5 bg-white/10 hover:bg-white/20 rounded-xl text-xs font-bold text-white transition-colors tracking-widest uppercase border border-white/5">Retry Engine</button>
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Loading Experience */}
              {isLoading && (
                <div className="bg-white p-16 rounded-[3rem] shadow-sm border border-slate-50 flex flex-col items-center">
                  <TransformationStepper currentStage={currentStage} />
                  <div className="mt-16 flex flex-col items-center space-y-8">
                    <div className="relative">
                      <div className="w-20 h-20 border-[6px] border-[#0f766e]/5 border-t-[#0f766e] rounded-full animate-spin" />
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-3 h-3 bg-[#0f766e] rounded-full animate-ping" />
                      </div>
                    </div>
                    <div className="text-center space-y-2">
                       <span className="text-2xl font-black text-slate-900 tracking-tight block">{loadingText}</span>
                       <div className="inline-flex items-center px-4 py-1 bg-teal-50 rounded-full border border-teal-100">
                         <p className="text-[10px] text-[#0f766e] font-black tracking-widest uppercase">Phase {currentStage} / 4</p>
                       </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Content Area */}
              {data && !error && !isLoading && (
                <div className="flex flex-col space-y-12">
                  <AnimatePresence mode="wait">
                    <motion.div
                      key={activeTab}
                      initial={{ opacity: 0, y: 10 }}
                      animate={{ opacity: 1, y: 0 }}
                      exit={{ opacity: 0, y: -10 }}
                      transition={{ duration: 0.2 }}
                      onAnimationComplete={() => completeStage(activeTab)}
                      className="max-w-4xl w-full mx-auto"
                    >
                      {activeTab === 'tamil' && <TamilCard content={data.tamil_simple} />}
                      {activeTab === 'english' && <EnglishCard content={data.english_academic} />}
                      {activeTab === 'steps' && <StepsCard steps={data.steps} />}
                      {activeTab === 'exam' && <DecoderCard decoder={data.question_decoder} />}
                      {activeTab === 'mcq' && <MCQSection mcqs={data.mcqs} />}
                    </motion.div>
                  </AnimatePresence>

                  {/* Progressive Unlock Action */}
                  <div className="flex justify-between items-center bg-white p-8 rounded-[2rem] border border-slate-100 shadow-sm relative overflow-hidden max-w-4xl w-full mx-auto">
                    <div className={`absolute top-0 left-0 bottom-0 w-2 transition-all duration-500 ${activeTab === 'mcq' ? 'bg-amber-400' : 'bg-teal-500/20'}`} />
                    <div>
                      <div className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-1">Status Report</div>
                      <div className="text-sm font-bold text-slate-900">
                        {activeTab === 'mcq' ? 'Final intelligence check active' : `Completing module ${['tamil', 'english', 'steps', 'exam', 'mcq'].indexOf(activeTab) + 1} of 5`}
                      </div>
                    </div>
                    
                    {activeTab !== 'mcq' && (
                      <button 
                        onClick={() => {
                          const tabs = ['tamil', 'english', 'steps', 'exam', 'mcq'];
                          const nextTab = tabs[tabs.indexOf(activeTab) + 1];
                          updateStage(nextTab as any);
                        }}
                        className="group flex items-center space-x-3 bg-[#0f766e] text-white px-10 py-4 rounded-2xl font-black shadow-xl shadow-teal-900/10 hover:bg-[#0d635c] transition-all transform hover:-translate-y-1 active:translate-y-0"
                      >
                        <span className="tracking-widest uppercase text-[10px]">Unlock Next Module</span>
                        <svg className="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M14 5l7 7m0 0l-7 7m7-7H3" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default function DashboardPage() {
  const [isLoading, setIsLoading] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [currentStage, setCurrentStage] = useState(0);
  const [loadingText, setLoadingText] = useState("");
  const [data, setData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const [conceptId, setConceptId] = useState("default");
  const [demoMode, setDemoMode] = useState(false);

  const handleTransform = async (text: string) => {
    // Generate a simple Unicode-safe hash for concept identification
    const encodedText = Array.from(new TextEncoder().encode(text.slice(0, 10)), (b) => String.fromCharCode(b)).join('');
    const newConceptId = btoa(encodedText).replace(/[^a-zA-Z0-9]/g, '') || `concept_${Date.now()}`;
    setConceptId(newConceptId);
    
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

      const response = await fetch("http://localhost:8000/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_input: text }),
      });

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
    } catch (err: any) {
      console.error("Engine failure:", err);
      setError(err.message || "An unexpected logic error occurred");
      setIsLoading(false);
    }
  };

  return (
    <LearningProvider initialConceptId={conceptId}>
      <main className="min-h-screen bg-slate-50 flex flex-col h-screen overflow-hidden">
        <Navbar />
        <DashboardContent 
          showResults={showResults} 
          setShowResults={setShowResults}
          isLoading={isLoading}
          handleTransform={handleTransform}
          error={error}
          data={data}
          loadingText={loadingText}
          currentStage={currentStage}
          demoMode={demoMode}
          setDemoMode={setDemoMode}
        />
      </main>
    </LearningProvider>
  );
}
