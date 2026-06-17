"use client"

import { useState } from "react"
import { Check, X, HelpCircle, Trophy } from "lucide-react"

interface MCQ {
  question: string
  options: string[]
  answer: number
  explanation: string
}

interface MCQSectionProps {
  mcqs: MCQ[]
}

export default function MCQSection({ mcqs }: MCQSectionProps) {
  const [currentIdx, setCurrentIdx] = useState(0)
  const [selected, setSelected] = useState<number | null>(null)
  const [showResult, setShowResult] = useState(false)
  const [score, setScore] = useState(0)

  if (!mcqs || mcqs.length === 0) return null

  const currentMcq = mcqs[currentIdx]
  const isCorrect = selected === currentMcq.answer

  const handleCheck = () => {
    if (selected === null) return
    setShowResult(true)
    if (isCorrect) setScore(s => s + 1)
  }

  const handleNext = () => {
    setSelected(null)
    setShowResult(false)
    setCurrentIdx(i => (i + 1) % mcqs.length)
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between border-b pb-4">
        <div className="flex items-center gap-2">
          <HelpCircle className="w-5 h-5 text-blue-500" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">Mastery Check</h3>
        </div>
        <div className="flex items-center gap-1 bg-green-50 px-3 py-1 rounded-full border border-green-100">
          <Trophy className="w-4 h-4 text-green-600" />
          <span className="text-sm font-bold text-green-700">{score}/{mcqs.length}</span>
        </div>
      </div>

      <div className="space-y-4">
        <p className="text-lg font-bold text-slate-800">{currentMcq.question}</p>
        
        <div className="grid gap-3">
          {currentMcq.options.map((option, idx) => {
            let variant = "border-slate-200 hover:border-blue-200 hover:bg-slate-50"
            if (showResult) {
              if (idx === currentMcq.answer) variant = "border-green-500 bg-green-50 text-green-700 font-bold"
              else if (selected === idx) variant = "border-red-500 bg-red-50 text-red-700"
              else variant = "opacity-50"
            } else if (selected === idx) {
              variant = "border-blue-500 bg-blue-50 text-blue-700 ring-2 ring-blue-500/10"
            }

            return (
              <button
                key={idx}
                disabled={showResult}
                onClick={() => setSelected(idx)}
                className={`p-4 rounded-xl border text-left transition-all flex items-center justify-between group ${variant}`}
              >
                <span>{option}</span>
                {showResult && idx === currentMcq.answer && <Check className="w-5 h-5 text-green-600" />}
                {showResult && selected === idx && idx !== currentMcq.answer && <X className="w-5 h-5 text-red-600" />}
              </button>
            )
          })}
        </div>

        {showResult ? (
          <div className={`p-4 rounded-xl ${isCorrect ? 'bg-green-50 border-green-100' : 'bg-slate-50 border-slate-200'} border animate-in fade-in slide-in-from-top-2 duration-300`}>
            <p className="text-sm">
              <span className="font-bold underline decoration-2">{isCorrect ? 'EXCELLENT:' : 'EXPLANATION:'}</span>{' '}
              {currentMcq.explanation}
            </p>
            <button
              onClick={handleNext}
              className="mt-4 w-full py-2 bg-slate-900 text-white rounded-lg font-bold hover:bg-slate-800 transition-colors"
            >
              Next Question
            </button>
          </div>
        ) : (
          <button
            onClick={handleCheck}
            disabled={selected === null}
            className="w-full py-3 bg-blue-600 text-white rounded-xl font-bold hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md shadow-blue-500/10"
          >
            Check Answer
          </button>
        )}
      </div>
    </div>
  )
}
