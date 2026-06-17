"use client"

import { useState, useRef, useEffect } from "react"
import { Search, Globe, Loader2 } from "lucide-react"
import { useCommandCenterStore } from "@/store/commandCenterStore"
import { fetchFullFlow } from "@/lib/api/fullFlow"

export default function TopQueryBar() {
  const { 
    query, setQuery, 
    language, setLanguage,
    activeRequestId, setActiveRequestId,
    cache, addToCache, hydrateFromCache,
    setLearn, setNavigator, setCoach
  } = useCommandCenterStore()

  const [localQuery, setLocalQuery] = useState(query)
  const abortControllerRef = useRef<AbortController | null>(null)
  const prevQueryRef = useRef<string>("")

  const handleSearch = async (e?: React.FormEvent) => {
    e?.preventDefault()
    const trimmedQuery = localQuery.trim()
    if (!trimmedQuery) return

    setQuery(trimmedQuery)
    const cacheKey = trimmedQuery.toLowerCase()
    
    // 1. Cache Check
    const cached = cache[cacheKey]
    if (cached && Date.now() - cached.timestamp < 600000) {
      hydrateFromCache(cached.data)
      return
    }

    // 2. Setup New Request
    if (abortControllerRef.current) abortControllerRef.current.abort()
    const controller = new AbortController()
    abortControllerRef.current = controller

    const requestId = Date.now().toString()
    setActiveRequestId(requestId)

    // 3. Set Loading States (Granular)
    setLearn(null, true)
    setNavigator(null, true)
    setCoach(null, false) 

    try {
      const res = await fetchFullFlow(trimmedQuery, controller.signal)

      // 4. Stale Response Protection
      if (useCommandCenterStore.getState().activeRequestId !== requestId) return

      // 5. Update Store & Cache
      setLearn(res.learning)
      setCoach(res.evaluation)
      setNavigator(res.navigator)
      addToCache(trimmedQuery, res)

      // 6. Subtle Auto-scroll for "system responded" feeling (Only on new query)
      if (prevQueryRef.current !== trimmedQuery) {
        setTimeout(() => {
          window.scrollTo({ top: 100, behavior: "smooth" })
        }, 100)
        prevQueryRef.current = trimmedQuery
      }

    } catch (err: any) {
      if (err.name === 'AbortError') return
      
      if (useCommandCenterStore.getState().activeRequestId === requestId) {
        setLearn(null, false, "Failed to load learning module")
        setNavigator(null, false, "Failed to load navigator")
      }
    }
  }

  // Trigger search on language change if query exists
  useEffect(() => {
    if (query) handleSearch()
  }, [language])

  return (
    <div className="flex items-center gap-4">
      <form onSubmit={handleSearch} className="flex-1 relative">
        <div className="relative group">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-400 group-focus-within:text-blue-500 transition-colors" />
          <input
            type="text"
            value={localQuery}
            onChange={(e) => setLocalQuery(e.target.value)}
            placeholder="Ask anything (e.g., Photosynthesis processes, Scholarships...)"
            className="w-full pl-10 pr-4 py-2.5 bg-slate-100 border-none rounded-xl focus:ring-2 focus:ring-blue-500/20 focus:bg-white transition-all outline-none text-slate-700 font-medium"
          />
        </div>
      </form>

      <div className="flex items-center bg-slate-100 p-1 rounded-xl border border-slate-200 shadow-sm">
        <button
          onClick={() => setLanguage("ta")}
          className={`px-4 py-1.5 rounded-lg text-sm font-bold transition-all ${
            language === "ta" 
              ? "bg-white text-blue-600 shadow-sm" 
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          தமிழ்
        </button>
        <button
          onClick={() => setLanguage("en")}
          className={`px-4 py-1.5 rounded-lg text-sm font-bold transition-all ${
            language === "en" 
              ? "bg-white text-blue-600 shadow-sm" 
              : "text-slate-500 hover:text-slate-700"
          }`}
        >
          English
        </button>
      </div>
    </div>
  )
}
