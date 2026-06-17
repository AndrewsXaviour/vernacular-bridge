'use client';

import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { LearningState, INITIAL_STATE, LearningEngine } from '../utils/learning-engine';

interface LearningContextType {
  state: LearningState;
  updateStage: (stage: LearningState['currentStage']) => void;
  completeStage: (stage: string) => void;
  updateMCQResult: (isCorrect: boolean, totalQuestions?: number) => void;
  incrementTime: () => void;
  resetForNewConcept: (conceptId: string) => void;
  goToStage: (stage: LearningState['currentStage']) => void;
  isResuming: boolean;
}

const LearningContext = createContext<LearningContextType | undefined>(undefined);

export function LearningProvider({ children, initialConceptId }: { children: React.ReactNode, initialConceptId: string }) {
  const [isResuming, setIsResuming] = useState(false);
  const [state, setState] = useState<LearningState>({
    ...INITIAL_STATE,
    conceptId: initialConceptId,
  });

  // Load from localStorage on mount
  useEffect(() => {
    const STORAGE_KEY = `vb_session_${initialConceptId}`;
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        if (parsed.conceptId === initialConceptId) {
          setState(parsed);
          setIsResuming(true);
          setTimeout(() => setIsResuming(false), 3000); // Hide toast after 3s
        }
      } catch (e) {
        console.error("Failed to parse saved state", e);
      }
    }
  }, [initialConceptId]);

  // Sync to localStorage
  useEffect(() => {
    const STORAGE_KEY = `vb_session_${state.conceptId}`;
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const updateStage = useCallback((stage: LearningState['currentStage']) => {
    setState(prev => ({
      ...prev,
      currentStage: stage,
    }));
  }, []);

  const goToStage = useCallback((stage: LearningState['currentStage']) => {
    setState(prev => ({ ...prev, currentStage: stage }));
  }, []);

  const completeStage = useCallback((stage: string) => {
    setState(prev => {
      if (prev.completedStages.includes(stage)) return prev;
      const newCompleted = [...prev.completedStages, stage];
      const newState = { ...prev, completedStages: newCompleted };
      return {
        ...newState,
        mastery: LearningEngine.calculateMastery(newState)
      };
    });
  }, []);

  const updateMCQResult = useCallback((isCorrect: boolean, totalQuestions?: number) => {
    setState(prev => {
      const totalAttempted = prev.currentQuestionIndex + 1;
      const currentCorrectCount = (prev.accuracy / 100) * prev.currentQuestionIndex;
      const newCorrectCount = isCorrect ? currentCorrectCount + 1 : currentCorrectCount;
      const newAccuracy = Math.round((newCorrectCount / totalAttempted) * 100);
      
      const isFinishing = totalQuestions ? totalAttempted >= totalQuestions : false;
      
      const newState = {
        ...prev,
        accuracy: newAccuracy,
        currentQuestionIndex: totalAttempted,
        isCompleted: isFinishing && prev.completedStages.length >= 4 
      };
      
      return {
        ...newState,
        mastery: LearningEngine.calculateMastery(newState)
      };
    });
  }, []);

  const incrementTime = useCallback(() => {
    setState(prev => ({ ...prev, timeSpent: prev.timeSpent + 1 }));
  }, []);

  const resetForNewConcept = useCallback((conceptId: string) => {
    const newState = {
      ...INITIAL_STATE,
      conceptId,
    };
    setState(newState);
    localStorage.setItem(`vb_session_${conceptId}`, JSON.stringify(newState));
  }, []);

  return (
    <LearningContext.Provider value={{ 
      state, 
      updateStage, 
      completeStage, 
      updateMCQResult, 
      incrementTime, 
      resetForNewConcept,
      goToStage,
      isResuming
    }}>
      {children}
    </LearningContext.Provider>
  );
}

export function useLearning() {
  const context = useContext(LearningContext);
  if (context === undefined) {
    throw new Error('useLearning must be used within a LearningProvider');
  }
  return context;
}
