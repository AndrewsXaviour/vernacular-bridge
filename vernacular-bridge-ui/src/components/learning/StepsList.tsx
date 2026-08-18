"use client"


interface StepsListProps {
  steps: string[]
}

export default function StepsList({ steps }: StepsListProps) {
  return (
    <div className="space-y-4">
      <h3 className="text-sm font-bold uppercase tracking-wider text-slate-500 mb-2">Process Transformation</h3>
      <div className="space-y-3">
        {steps.map((step, idx) => (
          <div key={idx} className="flex gap-4 p-4 bg-white border rounded-xl hover:border-blue-200 transition-colors group">
            <div className="flex-shrink-0 w-8 h-8 rounded-full bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-500 group-hover:bg-blue-100 group-hover:text-blue-600 transition-colors">
              {idx + 1}
            </div>
            <p className="text-slate-700 leading-snug pt-1 font-medium">
              {step}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}
