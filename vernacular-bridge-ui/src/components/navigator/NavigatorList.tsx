"use client"

import { FileText, Award, ChevronRight } from "lucide-react"
import { NavigatorItem } from "@/store/commandCenterStore"

interface NavigatorListProps {
  items: NavigatorItem[]
  selectedId: string | null
  onSelect: (id: string) => void
}

export default function NavigatorList({ items, selectedId, onSelect }: NavigatorListProps) {
  return (
    <div className="space-y-1">
      {items.map((item) => {
        const isSelected = selectedId === item.id
        const Icon = item.type === "entitlement" ? Award : FileText
        
        return (
          <button
            key={item.id}
            onClick={() => onSelect(item.id)}
            className={`w-full flex items-center gap-3 p-4 rounded-xl transition-all border text-left group ${
              isSelected 
                ? "bg-blue-600 border-blue-600 text-white shadow-lg shadow-blue-600/20" 
                : "bg-white border-transparent hover:border-slate-200 text-slate-600 hover:text-slate-900"
            }`}
          >
            <div className={`p-2 rounded-lg transition-colors ${
              isSelected ? "bg-white/20" : "bg-slate-100 group-hover:bg-blue-50"
            }`}>
              <Icon className="w-4 h-4" />
            </div>
            <div className="flex-1 overflow-hidden">
              <p className="font-bold text-sm truncate leading-tight">{item.title}</p>
              <p className={`text-[11px] truncate mt-0.5 ${
                isSelected ? "text-blue-100" : "text-slate-400"
              }`}>
                {item.description}
              </p>
            </div>
            <ChevronRight className={`w-4 h-4 transition-transform ${
              isSelected ? "translate-x-1" : "opacity-0 group-hover:opacity-100"
            }`} />
          </button>
        )
      })}
    </div>
  )
}
