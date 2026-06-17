"use client"

import TopQueryBar from "./TopQueryBar"
import LearningPanel from "./LearningPanel"
import CoachingPanel from "./CoachingPanel"
import NavigatorPanel from "./NavigatorPanel"

import { useCommandCenterStore } from "@/store/commandCenterStore"

export default function CommandCenterLayout() {
  const { activePanel } = useCommandCenterStore()

  return (
    <div className="flex flex-col h-screen bg-slate-50 text-slate-900">
      <header className="border-b bg-white px-6 py-4 shadow-sm z-10">
        <div className="max-w-7xl mx-auto">
          <TopQueryBar />
        </div>
      </header>

      <main className="flex-1 overflow-hidden relative">
        {activePanel === "learn" ? (
          <div className="h-full overflow-y-auto bg-white">
            <LearningPanel />
          </div>
        ) : activePanel === "coach" ? (
          <div className="h-full overflow-y-auto bg-white">
            <CoachingPanel />
          </div>
        ) : activePanel === "navigator" ? (
          <div className="h-full overflow-y-auto bg-slate-50">
            <NavigatorPanel />
          </div>
        ) : (
          <div className="h-full grid grid-cols-1 md:grid-cols-[1fr_1.2fr_0.8fr] gap-0 overflow-hidden">
            <section className="h-full overflow-y-auto border-r bg-white/50 backdrop-blur-sm">
              <LearningPanel />
            </section>
            <section className="h-full overflow-y-auto border-r bg-white text-slate-900">
              <CoachingPanel />
            </section>
            <section className="h-full overflow-y-auto bg-slate-50/50">
              <NavigatorPanel />
            </section>
          </div>
        )}
      </main>
    </div>
  )
}
