"use client"

import { Sparkles, Check, Copy } from "lucide-react"
import { useState } from "react"

interface ImprovedAnswerProps {
  content: string
}

export default function ImprovedAnswer({ content }: ImprovedAnswerProps) {
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(content)
    setCopied(true)
    setTimeout(() => setCopied(false), 2000)
  }

  return (
    <div className="p-6 bg-slate-900 text-slate-100 rounded-2xl border border-slate-800 shadow-xl shadow-purple-500/10">
      <div className="flex items-center gap-2 mb-4">
        <div className="px-2 py-1 bg-purple-500/20 text-purple-300 rounded flex items-center gap-1.5 font-bold text-[10px] uppercase tracking-widest border border-purple-500/30">
          <Sparkles className="w-3 h-3" />
          A.I. Refined Model
        </div>
      </div>
      
      <div className="prose prose-invert prose-slate max-w-none">
        <p className="text-[15px] leading-relaxed text-slate-300 font-medium whitespace-pre-wrap">
          {content}
        </p>
      </div>

      <div className="mt-6 pt-4 border-t border-slate-800 flex items-center justify-between">
        <span className="text-[10px] font-bold text-slate-500 uppercase">Recommended Academic Standard</span>
        <button 
          onClick={handleCopy}
          className="text-[10px] font-bold text-purple-400 hover:text-purple-300 transition-colors flex items-center gap-1.5 px-2 py-1 rounded hover:bg-purple-500/10"
        >
          {copied ? <Check className="w-3.5 h-3.5 text-green-400" /> : <Copy className="w-3.5 h-3.5" />}
          {copied ? <span className="text-green-400">COPIED!</span> : "COPY TO CLIPBOARD"}
        </button>
      </div>
    </div>
  )
}
