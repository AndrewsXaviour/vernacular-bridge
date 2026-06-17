"use client"

import { MessageSquare } from "lucide-react"

interface CoachTextAreaProps {
  value: string
  onChange: (val: string) => void
  loading?: boolean
}

export default function CoachTextArea({ value, onChange, loading }: CoachTextAreaProps) {
  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-purple-500" />
          <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500">Draft Your Answer</h3>
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
          placeholder="Type your explanation here to get real-time coaching..."
          className="w-full h-48 p-5 bg-purple-50/30 border border-purple-100 rounded-2xl focus:ring-4 focus:ring-purple-500/10 focus:bg-white focus:border-purple-300 transition-all outline-none text-slate-700 font-medium resize-none shadow-inner"
        />
        <div className="absolute right-4 bottom-4 text-[10px] font-bold text-slate-400 uppercase tracking-widest pointer-events-none">
          Live Feedback Enabled
        </div>
      </div>
    </div>
  )
}
