"use client"

import { Zap } from "lucide-react"

interface ScoreCardProps {
  score: number
  feedback: string
}

export default function ScoreCard({ score, feedback }: ScoreCardProps) {
  const getScoreColor = (s: number) => {
    if (s >= 80) return "text-green-600 bg-green-50 border-green-100"
    if (s >= 50) return "text-amber-600 bg-amber-50 border-amber-100"
    return "text-red-600 bg-red-50 border-red-100"
  }

  return (
    <div className={`p-6 rounded-2xl border transition-all duration-500 ${getScoreColor(score)}`}>
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-sm font-bold uppercase tracking-wider opacity-70">A.I. Rigor Score</h3>
        <div className="flex items-center gap-1 text-2xl font-black">
          <Zap className="w-6 h-6 fill-current" />
          {score}%
        </div>
      </div>
      
      <div className="space-y-2">
        <p className="text-sm font-bold opacity-80 uppercase tracking-tight">Pedagogical Feedback</p>
        <p className="text-[15px] font-medium leading-relaxed italic">
          "{feedback}"
        </p>
      </div>

      {/* Progress Bar */}
      <div className="mt-6 h-1 w-full bg-black/5 rounded-full overflow-hidden">
        <div 
          className="h-full bg-current transition-all duration-1000 ease-out" 
          style={{ width: `${score}%` }}
        />
      </div>
    </div>
  )
}
