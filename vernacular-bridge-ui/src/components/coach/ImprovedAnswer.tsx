"use client"

import { Sparkles } from "lucide-react"

interface ImprovedAnswerProps {
  content: string
}

export default function ImprovedAnswer({ content }: ImprovedAnswerProps) {
  return (
    <div className="p-6 bg-slate-900 text-slate-100 rounded-2xl border border-slate-800 shadow-2xl shadow-indigo-500/10">
      <div className="flex items-center gap-2 mb-4">
        <div className="p-1 px-2 border border-indigo-500/30 rounded text-indigo-400 flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-widest">
          <Sparkles className="w-3 h-3" />
          Refined Model
        </div>
      </div>
      
      <div className="prose prose-invert prose-slate max-w-none">
        <p className="text-[15px] leading-relaxed text-slate-300 font-medium">
          {content}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[10px] font-bold text-slate-500 uppercase">Recommended Academic Standard</span>
        <button className="text-[10px] font-bold text-indigo-400 hover:text-indigo-300 transition-colors flex items-center gap-1">
          COPY TO CLIPBOARD
        </button>
      </div>
    </div>
  )
}
