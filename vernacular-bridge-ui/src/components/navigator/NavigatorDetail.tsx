"use client"

import { NavigatorItem } from "@/store/commandCenterStore"
import { ExternalLink, Info } from "lucide-react"

interface NavigatorDetailProps {
  item: NavigatorItem
}

export default function NavigatorDetail({ item }: NavigatorDetailProps) {
  return (
    <div className="bg-white border rounded-2xl p-6 shadow-sm animate-in fade-in zoom-in-95 duration-300">
      <div className="flex items-start justify-between mb-6">
        <div>
          <span className={`inline-block px-2 py-0.5 rounded text-[10px] font-black uppercase tracking-wider mb-2 ${
            item.type === "entitlement" ? "bg-amber-100 text-amber-700" : "bg-blue-100 text-blue-700"
          }`}>
            {item.type}
          </span>
          <h3 className="text-xl font-black text-slate-800 leading-tight">
            {item.title}
          </h3>
        </div>
        <button className="p-2 bg-slate-50 rounded-full text-slate-400 hover:text-blue-600 hover:bg-blue-50 transition-all">
          <ExternalLink className="w-5 h-5" />
        </button>
      </div>

      <div className="space-y-4">
        <div className="flex gap-3 text-slate-600">
          <Info className="w-5 h-5 flex-shrink-0 text-slate-400 mt-0.5" />
          <p className="text-sm leading-relaxed font-medium">
            {item.description}
          </p>
        </div>

        <div className="pt-6 border-t border-slate-100">
          <h4 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4">Required Documents</h4>
          <div className="space-y-2">
            {["Identity Proof", "Address Proof", "Bank Passbook"].map((doc, idx) => (
              <div key={idx} className="flex items-center gap-2 text-xs font-bold text-slate-500 bg-slate-50 px-3 py-2 rounded-lg">
                <div className="w-1.5 h-1.5 rounded-full bg-slate-300" />
                {doc}
              </div>
            ))}
          </div>
        </div>

        <button className="w-full mt-4 py-3 bg-slate-900 text-white rounded-xl font-bold hover:bg-slate-800 transition-all shadow-lg shadow-slate-900/10 text-sm">
          Start Application Process
        </button>
      </div>
    </div>
  )
}
