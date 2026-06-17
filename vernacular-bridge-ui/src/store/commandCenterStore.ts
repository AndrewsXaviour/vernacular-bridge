"use client"

import { create } from "zustand"

export type LearnData = {
  tamil_simple: string
  english_academic: string
  steps: string[]
  mcqs: {
    question: string
    options: string[]
    answer: number
    explanation: string
  }[]
}

export type CoachData = {
  score: number
  feedback: string
  improved_answer: string
}

export type NavigatorItem = {
  id: string
  title: string
  description: string
  type: "process" | "entitlement"
}

export type NavigatorData = {
  items: NavigatorItem[]
}

interface PanelState<T> {
  data: T | null
  loading: boolean
  error: string | null
}

interface CacheEntry {
  timestamp: number
  data: {
    learning: LearnData
    evaluation: CoachData
    navigator: NavigatorData
  }
}

interface CommandCenterState {
  query: string
  language: "ta" | "en"
  activeRequestId: string | null

  learn: PanelState<LearnData>
  coach: {
    input: string
    data: CoachData | null
    loading: boolean
    error: string | null
  }
  navigator: {
    data: NavigatorData | null
    loading: boolean
    error: string | null
    selectedItemId: string | null
  }

  cache: Record<string, CacheEntry>
  activePanel: "learn" | "coach" | "navigator" | null

  // Actions
  setQuery: (query: string) => void
  setLanguage: (lang: "ta" | "en") => void
  setActiveRequestId: (id: string | null) => void
  setActivePanel: (panel: "learn" | "coach" | "navigator" | null) => void
  
  setLearn: (data: LearnData | null, loading?: boolean, error?: string | null) => void
  setCoach: (data: CoachData | null, loading?: boolean, error?: string | null) => void
  setCoachInput: (input: string) => void
  setNavigator: (data: NavigatorData | null, loading?: boolean, error?: string | null) => void
  setNavigatorSelectedId: (id: string | null) => void

  addToCache: (query: string, data: CacheEntry["data"]) => void
  hydrateFromCache: (data: CacheEntry["data"]) => void
}

export const useCommandCenterStore = create<CommandCenterState>((set, get) => ({
  query: "",
  language: "ta",
  activeRequestId: null,

  learn: { data: null, loading: false, error: null },
  coach: { input: "", data: null, loading: false, error: null },
  navigator: { data: null, loading: false, error: null, selectedItemId: null },

  cache: {},
  activePanel: null,

  setQuery: (query) => set({ query }),
  setLanguage: (language) => set({ language }),
  setActiveRequestId: (activeRequestId) => set({ activeRequestId }),
  setActivePanel: (activePanel) => set({ activePanel }),

  setLearn: (data, loading = false, error = null) => 
    set((s) => ({ learn: { ...s.learn, data, loading, error } })),

  setCoach: (data, loading = false, error = null) => 
    set((s) => ({ coach: { ...s.coach, data, loading, error } })),

  setCoachInput: (input) => set((s) => ({ coach: { ...s.coach, input } })),

  setNavigator: (data, loading = false, error = null) => 
    set((s) => ({ navigator: { ...s.navigator, data, loading, error } })),

  setNavigatorSelectedId: (selectedItemId) => 
    set((s) => ({ navigator: { ...s.navigator, selectedItemId } })),

  addToCache: (query, data) => {
    const key = query.trim().toLowerCase()
    set((s) => ({
      cache: {
        ...s.cache,
        [key]: {
          timestamp: Date.now(),
          data
        }
      }
    }))
  },

  hydrateFromCache: (data) => {
    set({
      learn: { data: data.learning as LearnData, loading: false, error: null },
      coach: { ...get().coach, data: data.evaluation as CoachData, loading: false, error: null },
      navigator: { ...get().navigator, data: data.navigator as NavigatorData, loading: false, error: null }
    })
  }
}))
