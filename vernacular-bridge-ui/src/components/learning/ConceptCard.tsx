"use client"

import { BookOpen } from "lucide-react"

interface ConceptCardProps {
  tamil_simple: string
  english_academic: string
}

export default function ConceptCard({ tamil_simple, english_academic }: ConceptCardProps) {
  return (
    <div className="space-y-6">
      <div className="p-5 bg-blue-50/50 border border-blue-100 rounded-2xl">
        <div className="flex items-center gap-2 mb-3">
          <div className="p-1.5 bg-blue-500 rounded-lg text-white">
            <BookOpen className="w-4 h-4" />
          </div>
          <h3 className="text-sm font-bold uppercase tracking-wider text-blue-600">Core Concept (Tamil)</h3>
        </div>
        <p className="text-lg text-slate-800 leading-relaxed font-medium">
          {tamil_simple}
        </p>
      </div>

      <div className="p-5 bg-indigo-50/50 border border-indigo-100 rounded-2xl">
        <h3 className="text-sm font-bold uppercase tracking-wider text-indigo-600 mb-3">Academic Definition (English)</h3>
        <p className="text-lg text-slate-800 leading-relaxed font-semibold font-serif italic">
          "{english_academic}"
        </p>
      </div>
    </div>
  )
}
