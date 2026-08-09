"use client"

import { useState, useRef } from "react"
import { useCommandCenterStore } from "@/store/commandCenterStore"
import { 
  ChevronDown, 
  ChevronUp, 
  Maximize2, 
  ArrowLeft, 
  CheckCircle2, 
  BookOpen, 
  Lightbulb, 
  Trophy 
} from "lucide-react"

export default function LearningPanel() {
  const { learn, query, activePanel, setActivePanel } = useCommandCenterStore()
  const [openSection, setOpenSection] = useState<string | null>("steps")
  const [selectedMCQ, setSelectedMCQ] = useState<number[]>(new Array(learn.data?.mcqs?.length || 0).fill(-1))
  const [understood, setUnderstood] = useState(false)
  
  const stepsRef = useRef<HTMLDivElement>(null)
  const academicRef = useRef<HTMLDivElement>(null)
  const mcqRef = useRef<HTMLDivElement>(null)

  // 10. LOADING STATE (SKELETON)
  if (learn.loading) {
    return (
      <div className="p-8 space-y-6 animate-pulse">
        <div className="h-8 w-48 bg-slate-200 rounded-lg" />
        <div className="space-y-3">
          <div className="h-4 w-full bg-slate-100 rounded" />
          <div className="h-4 w-5/6 bg-slate-100 rounded" />
        </div>
        <div className="h-40 w-full bg-slate-50 rounded-2xl" />
        <div className="h-40 w-full bg-slate-50 rounded-2xl" />
      </div>
    )
  }

  if (learn.error) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-12 text-center">
        <div className="w-16 h-16 rounded-full bg-red-50 flex items-center justify-center mb-4 text-red-500">
          <CheckCircle2 className="w-8 h-8 rotate-45" />
        </div>
        <h3 className="text-lg font-bold text-slate-800">Something went wrong</h3>
        <p className="text-slate-500 mt-2">{learn.error}</p>
      </div>
    )
  }

  if (!learn.data) {
    return (
      <div className="h-full flex flex-col items-center justify-center p-12 text-center text-slate-400">
        <div className="w-16 h-16 rounded-full bg-slate-50 flex items-center justify-center mb-4 border border-dashed border-slate-200">
          <BookOpen className="w-8 h-8" />
        </div>
        <h3 className="text-lg font-medium text-slate-600">No Content Selected</h3>
        <p className="mt-2 text-sm max-w-[240px]">Search for any topic to begin your bilingual learning journey.</p>
      </div>
    )
  }

  const { tamil_simple, english_academic, steps, mcqs } = learn.data
  
  // 1. SUMMARY SPLIT — MAKE IT SAFE
  const summary = tamil_simple?.slice(0, 180) + "..."

  const toggleSection = (section: string) => {
    // 2. ACCORDION — SIMPLE APPROACH
    setOpenSection(openSection === section ? null : section)
  }

  // 4. SCROLL BUTTONS — USE REF
  const scrollToSection = (ref: React.RefObject<HTMLDivElement | null>, section: string) => {
    setOpenSection(section)
    setTimeout(() => {
      ref.current?.scrollIntoView({ behavior: "smooth", block: "start" })
    }, 100)
  }


  return (
    <div className={`relative ${activePanel === "learn" ? "max-w-4xl mx-auto py-12 px-8" : "p-6"} space-y-8 animate-in fade-in duration-500`}>
      
      {/* 9. EXPAND BUTTON POSITION */}
      <div className="absolute top-2 right-2 flex items-center gap-2 z-20">
        {activePanel === "learn" ? (
          <button 
            onClick={() => setActivePanel(null)}
            className="flex items-center gap-2 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-slate-600 rounded-lg text-sm font-semibold transition-colors"
          >
            <ArrowLeft className="w-4 h-4" /> Back to workspace
          </button>
        ) : (
          <button 
            onClick={() => setActivePanel("learn")}
            className="p-2 hover:bg-slate-100 text-slate-400 hover:text-slate-600 rounded-lg transition-all"
            title="Expand to Focus Mode"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
        )}
      </div>

      {/* 1. HEADER */}
      <header className="space-y-1 pr-12">
        <h1 className="text-2xl md:text-3xl font-black text-slate-900 tracking-tight">
          {query}
        </h1>
        <p className="text-xs font-bold text-blue-500 uppercase tracking-widest">
          Cognitive Concept Node
        </p>
      </header>

      {/* 2. QUICK SUMMARY (TAMIL) with SMALL LABEL */}
      <section className="space-y-2">
        <p className="text-xs text-gray-500 font-medium">Simple Explanation (Tamil)</p>
        <p className="text-[17px] md:text-[18px] leading-7 md:leading-8 tracking-wide text-slate-800 font-medium">
          {summary}
        </p>
      </section>

      {/* 4. ACTION BUTTONS (MANDATORY) */}
      <div className="flex flex-wrap gap-2 pt-2">
        <button 
          onClick={() => scrollToSection(academicRef, "english")}
          className="px-4 py-2 bg-indigo-50 text-indigo-700 rounded-full text-sm font-bold hover:bg-indigo-100 transition-colors"
        >
          Show academic version
        </button>
        <button 
          onClick={() => scrollToSection(mcqRef, "mcq")}
          className="px-4 py-2 bg-purple-50 text-purple-700 rounded-full text-sm font-bold hover:bg-purple-100 transition-colors"
        >
          Test me
        </button>
      </div>

      {/* 3. ACCORDION STRUCTURE (CORE) */}
      <div className="space-y-4 pt-4 border-t border-slate-100">
        
        {/* SECTION 1: 🧩 Step-by-step Breakdown (DEFAULT OPEN) */}
        <div ref={stepsRef} className="overflow-hidden">
          <button 
            onClick={() => toggleSection("steps")}
            className="flex items-center justify-between w-full py-4 text-left group"
          >
            <h3 className="text-lg font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
              🧩 Step-by-step Breakdown
            </h3>
            {openSection === "steps" ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          
          {openSection === "steps" && (
            <div className="pb-6 space-y-4 animate-in slide-in-from-top-2 duration-300">
              <div className="space-y-3">
                {steps?.length > 0 && steps.map((step, i) => (
                  <div key={i} className="flex gap-4 items-start p-1">
                    <span className="flex-shrink-0 w-6 h-6 rounded-full bg-slate-100 text-slate-500 text-xs font-bold flex items-center justify-center mt-1">
                      {i + 1}
                    </span>
                    <p className="text-[16px] text-slate-700 leading-7 md:leading-8 tracking-wide">
                      {step}
                    </p>
                  </div>
                ))}
              </div>
              
              {/* ⚡ 1. ADD “YOU UNDERSTOOD” BUTTON */}
              <button 
                onClick={() => setUnderstood(!understood)}
                className={`mt-4 flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-bold transition-all ${
                  understood 
                    ? "bg-green-100 text-green-700 shadow-sm" 
                    : "text-green-600 hover:bg-green-50"
                }`}
              >
                <CheckCircle2 className={`w-4 h-4 ${understood ? "fill-green-700 text-white" : ""}`} />
                {understood ? "I understood this" : "✔ I understood this"}
              </button>
            </div>
          )}
        </div>

        {/* SECTION 2: 📘 Academic English */}
        <div ref={academicRef} className="border-t border-slate-100">
          <button 
            onClick={() => toggleSection("english")}
            className="flex items-center justify-between w-full py-4 text-left group"
          >
            <h3 className="text-lg font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
              📘 Academic Version (English)
            </h3>
            {openSection === "english" ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          
          {openSection === "english" && (
            <div className="pb-6 animate-in slide-in-from-top-2 duration-300">
              <p className="text-xs text-gray-500 font-medium mb-3">Academic Version (English)</p>
              <p className="italic text-gray-700 leading-7 md:leading-8 tracking-wide bg-slate-50/50 p-6 rounded-2xl border-l-4 border-slate-200">
                "{english_academic}"
              </p>
            </div>
          )}
        </div>

        {/* SECTION 3: 📝 Quick Test (MCQ) — 8. MCQ ABOVE FOLD */}
        <div ref={mcqRef} className="border-t border-slate-100">
          <button 
            onClick={() => toggleSection("mcq")}
            className="flex items-center justify-between w-full py-4 text-left group"
          >
            <h3 className="text-lg font-bold text-slate-800 group-hover:text-blue-600 transition-colors">
              📝 Quick Test (Assessment)
            </h3>
            {openSection === "mcq" ? <ChevronUp className="w-5 h-5 text-slate-400" /> : <ChevronDown className="w-5 h-5 text-slate-400" />}
          </button>
          
          {openSection === "mcq" && (
            <div className="pb-8 space-y-8 animate-in slide-in-from-top-2 duration-300">
              {mcqs?.length > 0 ? (
                mcqs.map((mcq, qIdx) => (
                  <div key={qIdx} className="space-y-4">
                    <p className="text-[16px] font-bold text-slate-800 pr-4">
                      {qIdx + 1}. {mcq.question}
                    </p>
                    <div className="grid grid-cols-1 gap-2">
                    {/* ⚡ 3. MCQ — MUST FEEL INSTANT */}
                      {mcq.options.map((opt, oIdx) => {
                        const isCorrect = opt === (mcq as any).correct_answer || oIdx === (mcq as any).answer;
                        const isSelected = selectedMCQ[qIdx] === oIdx;
                        const showResult = selectedMCQ[qIdx] !== -1;
                        
                        return (
                          <button
                            key={oIdx}
                            disabled={showResult}
                            onClick={() => {
                              const newSelected = [...selectedMCQ]
                              newSelected[qIdx] = oIdx
                              setSelectedMCQ(newSelected)
                            }}
                            className={`w-full text-left p-4 rounded-xl text-sm font-medium transition-all border-2 ${
                              isSelected
                                ? isCorrect 
                                  ? "bg-green-50 border-green-500 text-green-700" 
                                  : "bg-red-50 border-red-500 text-red-700"
                                : showResult && isCorrect
                                  ? "bg-green-50 border-green-200 text-green-700"
                                  : "bg-white border-slate-100 hover:border-slate-300 text-slate-600"
                            }`}
                          >
                            <div className="flex items-center gap-3">
                              <span className="w-6 h-6 rounded-full border flex items-center justify-center text-[10px] font-bold uppercase">
                                {String.fromCharCode(65 + oIdx)}
                              </span>
                              {opt}
                            </div>
                          </button>
                        )
                      })}
                    </div>
                    {selectedMCQ[qIdx] !== -1 && (
                      <div className="space-y-3 animate-in fade-in duration-500">
                        <div className="flex items-center gap-2 p-3 bg-slate-50 rounded-lg">
                          <Trophy className="w-4 h-4 text-amber-500" />
                          <p className="text-[11px] font-bold text-slate-500 uppercase tracking-tight">
                            You’re improving your academic understanding
                          </p>
                        </div>
                        {/* ⚡ 1. ADD “SMALL PROGRESS FEEL” (VERY LIGHT) */}
                        <p className="text-xs text-gray-500 px-1">
                          Keep exploring other sections to master the concept.
                        </p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <p className="text-sm text-slate-400 italic">No practice questions available for this topic.</p>
              )}
            </div>
          )}
        </div>

      </div>
    </div>
  )
}
