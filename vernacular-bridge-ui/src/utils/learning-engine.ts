/**
 * LearningEngine Utility
 * Encapsulates pedagogical logic for mastery calculation, progression, and accuracy.
 */

export interface LearningState {
  currentStage: "tamil" | "english" | "steps" | "exam" | "mcq";
  completedStages: string[];
  mastery: number;
  accuracy: number;
  timeSpent: number;
  currentQuestionIndex: number;
  conceptId: string;
  isCompleted: boolean;
}

export const INITIAL_STATE: Omit<LearningState, 'conceptId'> = {
  currentStage: "tamil",
  completedStages: [],
  mastery: 0,
  accuracy: 0,
  timeSpent: 0,
  currentQuestionIndex: 0,
  isCompleted: false,
};

export class LearningEngine {
  static academicKeywords = [
    "Photosynthesis",
    "Chlorophyll",
    "ATP",
    "NADPH",
    "Calvin Cycle",
    "Glucose",
    "Carbon Dioxide",
    "Oxygen",
    "Synthesis",
    "Photon",
    "Electron",
    "Enzyme"
  ];

  static tooltips: Record<string, string> = {
    "Photosynthesis": "The process by which green plants use sunlight to synthesize nutrients.",
    "ATP": "Adenosine Triphosphate: The primary energy carrier in all living organisms.",
    "Chlorophyll": "The green pigment in plants responsible for absorbing light energy.",
    "NADPH": "An electron carrier that provides the high-energy electrons needed for synthesis.",
    "Calvin Cycle": "The set of chemical reactions that take place in chloroplasts during photosynthesis.",
    "Glucose": "A simple sugar that is an important energy source in living organisms.",
    "Carbon Dioxide": "A gas used by plants to produce sugars during photosynthesis.",
    "Oxygen": "A byproduct of photosynthesis released into the atmosphere.",
    "Synthesis": "The production of chemical compounds by reaction from simpler materials.",
    "Photon": "A particle representing a quantum of light.",
    "Enzyme": "A substance that acts as a catalyst in living organisms."
  };

  static getTooltip(word: string): string | null {
    const cleanWord = word.replace(/[^a-zA-Z]/g, '');
    return this.tooltips[cleanWord] || this.tooltips[Object.keys(this.tooltips).find(k => k.toLowerCase() === cleanWord.toLowerCase()) || ""] || null;
  }

  static calculateMastery(state: LearningState): number {
    const stageWeight = 15; // Each stage completion gives 15%
    const mcqWeight = 25;   // Total MCQ accuracy gives up to 25%
    
    const progressMastery = state.completedStages.length * stageWeight;
    const accuracyMastery = (state.accuracy / 100) * mcqWeight;
    
    return Math.min(100, Math.round(progressMastery + accuracyMastery));
  }

  /**
   * Generates pedagogical insights based on state.
   */
  static getInsight(state: LearningState): string {
    if (state.mastery < 20) return "Starting your mapping. Focus on the core Tamil meaning first.";
    if (state.mastery < 50) return "Gaining clarity. Pay close attention to the academic terminology bridge.";
    if (state.accuracy < 60 && state.currentQuestionIndex > 0) return "Terminology is solid, but look closer at the logical sequence.";
    if (state.accuracy >= 80 && state.mastery > 70) return "Strong conceptual mastery! You are ready for exam-level application.";
    if (state.completedStages.includes('exam')) return "Academic structure established. Finalizing intelligence check.";
    return "Consolidating knowledge. Review the steps if the sequence feels complex.";
  }

  static isStageUnlocked(stage: string, state: LearningState): boolean {
    const progression = ["tamil", "english", "steps", "exam", "mcq"];
    const stageIndex = progression.indexOf(stage);
    
    if (stageIndex <= 0) return true; // Tamil is always unlocked
    
    const previousStage = progression[stageIndex - 1];
    return state.completedStages.includes(previousStage);
  }

  static getNextStage(currentStage: string): string | null {
    const progression = ["tamil", "english", "steps", "exam", "mcq"];
    const currentIndex = progression.indexOf(currentStage);
    
    if (currentIndex < progression.length - 1) {
      return progression[currentIndex + 1];
    }
    return null;
  }
}
