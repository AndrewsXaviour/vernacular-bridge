"use client"

import { useEffect, useRef } from "react"
import { useCommandCenterStore } from "@/store/commandCenterStore"
import { fetchCoach } from "@/lib/api/coach"
import CoachTextArea from "../coach/CoachTextArea"
import ScoreCard from "../coach/ScoreCard"
import ImprovedAnswer from "../coach/ImprovedAnswer"
import { Loader2, Sparkles, Maximize2, ArrowLeft } from "lucide-react"

export default function CoachingPanel() {
  const { query, coach, setCoachInput, setCoach, activePanel, setActivePanel } = useCommandCenterStore()
  const { input, data, loading, error } = coach
  const abortControllerRef = useRef<AbortController | null>(null)
  const lastRequestRef = useRef<string>("")

  useEffect(() => {
    if (!input || input.trim().length < 5) {
      setCoach(null, false)
      return
    }

    const t = setTimeout(async () => {
      if (abortControllerRef.current) abortControllerRef.current.abort()
      const controller = new AbortController()
      abortControllerRef.current = controller

      const currentRequestId = Date.now().toString()
      lastRequestRef.current = currentRequestId

      setCoach(data, true)

      // ⚠️ Use simplified prompt logic
      const question = query.length < 10 ? `Explain ${query}` : query

      try {
        const res = await fetchCoach(question, input, controller.signal)
        
        if (lastRequestRef.current === currentRequestId) {
          // ⚠️ Map backend structure_feedback to frontend feedback
          const mappedData = {
            ...res,
            feedback: res.structure_feedback || res.feedback
          }
          setCoach(mappedData, false)
        }
      } catch (err: any) {
        if (err.name === 'AbortError') return
        if (lastRequestRef.current === currentRequestId) {
          setCoach(data, false, "Failed to analyze answer")
        }
      }
    }, 800)

    return () => clearTimeout(t)
  }, [input])

  return (
    <div className={`h-full flex flex-col ${activePanel === "coach" ? "max-w-4xl mx-auto" : ""}`}>
      <div className="p-6 border-b flex items-center justify-between bg-white sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Sparkles className="w-5 h-5 text-purple-500 fill-purple-500" />
          <h2 className="text-xl font-black text-slate-800 tracking-tight">Writing Coach</h2>
        </div>
        <div className="flex items-center gap-2">
          {activePanel === "coach" ? (
            <button 
              onClick={() => setActivePanel(null)}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm font-semibold transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          ) : (
            <button 
              onClick={() => setActivePanel("coach")}
              className="p-2 hover:bg-slate-100 text-slate-400 hover:text-slate-600 rounded-lg transition-all"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 p-6 space-y-8 pb-12 overflow-y-auto">
        {/* Flow Hint */}
        <div className="animate-in fade-in slide-in-from-left-4 duration-700">
          <p className="text-xs font-bold text-purple-600 uppercase tracking-widest flex items-center gap-2">
            Next: Try writing this in English 
            <span className="animate-bounce-x">→</span>
          </p>
        </div>

        {/* Input Area */}
        <CoachTextArea 
          value={input} 
          onChange={setCoachInput} 
          loading={loading}
        />

        {/* Results Area */}
        {data ? (
          <div className="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
            <ScoreCard 
              score={data.score} 
              feedback={data.feedback} 
            />
            <ImprovedAnswer 
              content={data.improved_answer} 
            />
          </div>
        ) : !loading && input.trim().length > 0 && input.trim().length < 5 ? (
          <div className="p-8 text-center border-2 border-dashed border-slate-100 rounded-2xl grayscale opacity-50">
            <p className="text-sm font-bold text-slate-400">INPUT TOO SHORT FOR ANALYSIS</p>
          </div>
        ) : !loading && !data && (
          <div className="p-12 text-center space-y-4 rounded-2xl bg-slate-50 border border-slate-100">
            <div className="w-12 h-12 rounded-full bg-white shadow-sm flex items-center justify-center mx-auto text-slate-300">
              <Sparkles className="w-6 h-6" />
            </div>
            <p className="text-sm text-slate-500 font-medium leading-relaxed">
              Based on what you learned, write an explanation.<br />
              <span className="text-purple-600 font-bold italic">We'll help you refine the academic tone.</span>
            </p>
          </div>
        )}

        {error && (
          <div className="p-4 bg-red-50 border border-red-100 rounded-xl text-red-600 text-sm font-medium">
            {error}
          </div>
        )}
      </div>
    </div>
  )
}
