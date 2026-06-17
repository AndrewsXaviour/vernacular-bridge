import React from 'react';
import { motion } from 'framer-motion';
import { useLearning } from '@/context/LearningContext';
import { LearningEngine } from '@/utils/learning-engine';
import { 
  Languages, 
  GraduationCap, 
  ListOrdered, 
  Trophy, 
  BrainCircuit,
  CheckCircle,
  Lock,
  Zap,
  BookOpen
} from 'lucide-react';

export default function DashboardSidebar() {
  const { state, updateStage } = useLearning();
  const { currentStage: activeTab, completedStages, mastery, accuracy, timeSpent } = state;

  const stages = [
    { id: 'tamil', label: 'Tamil Understanding', icon: <Languages className="w-4 h-4" /> },
    { id: 'english', label: 'Academic English', icon: <GraduationCap className="w-4 h-4" /> },
    { id: 'steps', label: 'Step-by-Step Logic', icon: <ListOrdered className="w-4 h-4" /> },
    { id: 'exam', label: 'Exam Strategy', icon: <Trophy className="w-4 h-4" /> },
    { id: 'mcq', label: 'Intelligence Check', icon: <BrainCircuit className="w-4 h-4" /> },
  ];

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = seconds % 60;
    return `${mins}m ${secs}s`;
  };

  const insight = LearningEngine.getInsight(state);

  return (
    <aside className="h-full bg-white border-r border-slate-100 p-8 flex flex-col font-outfit">
      {/* Brand */}
      <div className="flex items-center space-x-3 mb-10">
        <div className="bg-[#0f766e] p-2.5 rounded-2xl shadow-lg shadow-teal-900/10">
          <BookOpen className="w-6 h-6 text-white" />
        </div>
        <span className="text-xl font-black text-slate-900 tracking-tight">Vernacular Bridge</span>
      </div>

      {/* Progress Ring */}
      <div className="mb-10 relative flex flex-col items-center">
        <div className="relative w-36 h-36">
          <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
            <circle className="text-slate-100 stroke-current" strokeWidth="6" fill="transparent" r="44" cx="50" cy="50" />
            <motion.circle 
              className="text-[#0f766e] stroke-current" 
              strokeWidth="6" 
              strokeLinecap="round" 
              fill="transparent" 
              r="44" 
              cx="50" 
              cy="50" 
              initial={{ strokeDasharray: "0, 276.5" }}
              animate={{ strokeDasharray: `${(mastery / 100) * 276.5}, 276.5` }}
              transition={{ duration: 1.5, ease: "easeOut" }}
            />
          </svg>
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            <span className="text-3xl font-black text-slate-900">{mastery}%</span>
            <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Mastery</span>
          </div>
        </div>
        
        {/* Tutor Insight */}
        <div className="mt-6 w-full p-4 bg-teal-50/50 rounded-2xl border border-teal-100/30 flex items-start space-x-3">
          <div className="bg-[#0f766e]/10 p-1.5 rounded-lg text-[#0f766e]">
            <Zap className="w-3.5 h-3.5" />
          </div>
          <p className="text-[11px] font-bold text-slate-600 leading-relaxed">
            <span className="uppercase text-[8px] font-black text-[#0f766e] block mb-1 tracking-widest opacity-70">Tutor Insight</span>
            {insight}
          </p>
        </div>
      </div>

      {/* Learning Path */}
      <div className="flex-grow space-y-2.5">
        {stages.map((stage) => {
          const isCompleted = completedStages.includes(stage.id);
          const isActive = activeTab === stage.id;
          const isLocked = !LearningEngine.isStageUnlocked(stage.id, state);

          return (
            <button
              key={stage.id}
              disabled={isLocked}
              onClick={() => updateStage(stage.id as any)}
              className={`w-full group relative flex items-center p-3.5 rounded-2xl transition-all duration-300
                ${isActive ? 'bg-[#0f766e] text-white shadow-xl shadow-teal-900/15 ring-1 ring-teal-600' : 
                  isLocked ? 'opacity-30 cursor-not-allowed' : 
                  'bg-white text-slate-500 hover:bg-slate-50'}
              `}
            >
              <div className={`p-2 rounded-xl mr-3 ${isActive ? 'bg-white/10' : 'bg-slate-100 group-hover:bg-white'} transition-colors`}>
                {stage.icon}
              </div>
              <span className={`text-[13px] font-black tracking-tight ${isActive ? 'text-white' : 'text-slate-600'}`}>
                {stage.label}
              </span>
              {isCompleted && !isActive && (
                <CheckCircle className="w-3.5 h-3.5 text-teal-500 ml-auto" />
              )}
              {isLocked && !isActive && (
                <Lock className="w-3 h-3 text-slate-300 ml-auto" />
              )}
            </button>
          );
        })}
      </div>

      {/* Footer Stats */}
      <div className="mt-8 pt-8 border-t border-slate-50 grid grid-cols-2 gap-4">
        <div className="space-y-1">
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Accuracy</span>
          <div className="text-[13px] font-black text-slate-900">{accuracy}%</div>
        </div>
        <div className="space-y-1">
          <span className="text-[9px] font-black text-slate-400 uppercase tracking-[0.2em]">Time Spent</span>
          <div className="text-[13px] font-black text-slate-900">{formatTime(timeSpent)}</div>
        </div>
      </div>
    </aside>
  );
}
