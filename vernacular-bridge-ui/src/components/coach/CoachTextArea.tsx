"use client"

import { MessageSquare, Sparkles, Send } from "lucide-react"

interface CoachTextAreaProps {
  value: string
  onChange: (val: string) => void
  onSubmit: () => void
  loading?: boolean
}

export default function CoachTextArea({ value, onChange, onSubmit, loading }: CoachTextAreaProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-purple-600" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-600">Draft Your Answer</h3>
        </div>
        {loading && (
          <div className="flex items-center gap-2 text-xs font-bold text-purple-600 animate-pulse">
            <span className="w-2 h-2 rounded-full bg-purple-500 animate-ping" />
            Analyzing...
          </div>
        )}
      </div>
      
      <div className="relative group">
        <textarea
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder="Type your explanation here..."
          className="w-full h-48 p-5 pb-16 bg-purple-50/30 border border-purple-100 rounded-2xl focus:ring-4 focus:ring-purple-500/10 focus:bg-white focus:border-purple-300 transition-all outline-none text-slate-700 font-medium resize-none shadow-inner"
        />
        <div className="absolute right-4 bottom-4 flex items-center gap-4">
          <span className="text-[10px] font-bold text-slate-400 uppercase tracking-widest pointer-events-none">
            {value.length} characters
          </span>
          <button
            onClick={onSubmit}
            disabled={loading || value.trim().length < 5}
            className="flex items-center gap-2 bg-purple-600 hover:bg-purple-700 disabled:bg-purple-300 text-white px-5 py-2.5 rounded-xl text-sm font-bold shadow-sm shadow-purple-600/20 transition-all hover:-translate-y-0.5 active:translate-y-0 disabled:transform-none disabled:cursor-not-allowed"
          >
            {loading ? (
              <Sparkles className="w-4 h-4 animate-spin" />
            ) : (
              <Send className="w-4 h-4" />
            )}
            <span>Analyze Answer</span>
          </button>
        </div>
      </div>
    </div>
  )
}
