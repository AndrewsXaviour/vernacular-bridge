"use client"

import { Zap, CheckCircle2, AlertTriangle, Lightbulb, TrendingUp } from "lucide-react"

interface ScoreCardProps {
  score: number
  strengths?: string[]
  weaknesses?: string[]
  missing_points?: string[]
  improvement_suggestions?: string[]
}

export default function ScoreCard({ 
  score, 
  strengths = [], 
  weaknesses = [], 
  missing_points = [], 
  improvement_suggestions = [] 
}: ScoreCardProps) {
  
  const getScoreColor = (s: number) => {
    if (s >= 7) return "text-green-700 bg-green-50 border-green-200"
    if (s >= 5) return "text-amber-700 bg-amber-50 border-amber-200"
    return "text-red-700 bg-red-50 border-red-200"
  }

  const getScoreLabel = (s: number) => {
    if (s >= 9) return "Excellent"
    if (s >= 7) return "Good"
    if (s >= 5) return "Adequate"
    if (s >= 3) return "Partial Understanding"
    return "Significant Gaps"
  }

  const percentage = Math.min(Math.max((score / 10) * 100, 0), 100)

  return (
    <div className={`p-6 rounded-2xl border transition-all duration-500 shadow-sm ${getScoreColor(score)}`}>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-xs font-bold uppercase tracking-wider opacity-80 mb-1">A.I. Rigor Score</h3>
          <p className="text-sm font-semibold opacity-90">{getScoreLabel(score)}</p>
        </div>
        <div className="flex items-end gap-1 font-black">
          <Zap className="w-8 h-8 fill-current" />
          <span className="text-4xl leading-none">{score}</span>
          <span className="text-xl opacity-60 leading-none mb-1">/10</span>
        </div>
      </div>
      
      {/* Progress Bar */}
      <div className="mb-8 h-2 w-full bg-black/10 rounded-full overflow-hidden">
        <div 
          className="h-full bg-current transition-all duration-1000 ease-out rounded-full" 
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Strengths & Weaknesses */}
        <div className="space-y-4">
          {strengths.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 text-sm font-bold uppercase tracking-tight mb-2">
                <CheckCircle2 className="w-4 h-4" /> Strengths
              </h4>
              <ul className="space-y-1.5">
                {strengths.map((item, i) => (
                  <li key={i} className="text-sm font-medium opacity-90 leading-snug flex items-start gap-2">
                    <span className="mt-1 opacity-50">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {weaknesses.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 text-sm font-bold uppercase tracking-tight mb-2 mt-4">
                <AlertTriangle className="w-4 h-4" /> Weaknesses
              </h4>
              <ul className="space-y-1.5">
                {weaknesses.map((item, i) => (
                  <li key={i} className="text-sm font-medium opacity-90 leading-snug flex items-start gap-2">
                    <span className="mt-1 opacity-50">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {/* Missing Points & Suggestions */}
        <div className="space-y-4">
          {missing_points.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 text-sm font-bold uppercase tracking-tight mb-2">
                <Lightbulb className="w-4 h-4" /> Missing Key Points
              </h4>
              <ul className="space-y-1.5">
                {missing_points.map((item, i) => (
                  <li key={i} className="text-sm font-medium opacity-90 leading-snug flex items-start gap-2">
                    <span className="mt-1 opacity-50">•</span>
                    <span>{item}</span>
                  </li>
                ))}
              </ul>
            </div>
          )}

          {improvement_suggestions.length > 0 && (
            <div>
              <h4 className="flex items-center gap-2 text-sm font-bold uppercase tracking-tight mb-2 mt-4">
                <TrendingUp className="w-4 h-4" /> How to Improve
              </h4>
              <ul className="space-y-2">
                {improvement_suggestions.map((item, i) => (
                  <li key={i} className="text-sm font-medium bg-white/40 p-3 rounded-xl leading-snug shadow-sm border border-black/5">
                    {item}
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
