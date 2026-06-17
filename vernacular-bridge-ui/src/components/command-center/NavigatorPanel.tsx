import { useCommandCenterStore } from "@/store/commandCenterStore"
import NavigatorList from "../navigator/NavigatorList"
import NavigatorDetail from "../navigator/NavigatorDetail"
import { Compass, Loader2, Search, Maximize2, ArrowLeft, Star } from "lucide-react"

export default function NavigatorPanel() {
  const { navigator, setNavigatorSelectedId, activePanel, setActivePanel } = useCommandCenterStore()
  const { data, loading, error, selectedItemId } = navigator

  const selectedItem = data?.items.find(i => i.id === selectedItemId)

  return (
    <div className={`h-full flex flex-col ${activePanel === "navigator" ? "max-w-4xl mx-auto" : ""}`}>
      <div className="p-6 border-b flex items-center justify-between bg-slate-50 sticky top-0 z-10">
        <div className="flex items-center gap-2">
          <Compass className="w-5 h-5 text-blue-600" />
          <h2 className="text-xl font-black text-slate-800 tracking-tight">Navigation Engine</h2>
        </div>
        <div className="flex items-center gap-2">
          {activePanel === "navigator" ? (
            <button 
              onClick={() => setActivePanel(null)}
              className="flex items-center gap-2 px-3 py-1.5 bg-slate-200 hover:bg-slate-300 text-slate-700 rounded-lg text-sm font-semibold transition-colors"
            >
              <ArrowLeft className="w-4 h-4" /> Back
            </button>
          ) : (
            <button 
              onClick={() => setActivePanel("navigator")}
              className="p-2 hover:bg-slate-200 text-slate-400 hover:text-slate-600 rounded-lg transition-all"
            >
              <Maximize2 className="w-5 h-5" />
            </button>
          )}
        </div>
      </div>

      <div className="flex-1 p-4 space-y-6 overflow-y-auto pb-12">
        {loading ? (
          <div className="p-12 flex flex-col items-center justify-center text-slate-400">
            <Loader2 className="w-8 h-8 animate-spin mb-3 text-blue-500" />
            <p className="text-xs font-bold uppercase tracking-widest animate-pulse">Scanning DB...</p>
          </div>
        ) : error ? (
          <div className="p-6 bg-red-50 border border-red-100 rounded-xl">
            <p className="text-sm font-bold text-red-600 uppercase tracking-tight">Access Error</p>
            <p className="text-xs text-red-500 mt-1">{error}</p>
          </div>
        ) : data && data.items.length > 0 ? (
          <div className="space-y-6">
            <section>
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-4 px-2">Matched Results</h3>
              <NavigatorList 
                items={data.items} 
                selectedId={selectedItemId} 
                onSelect={setNavigatorSelectedId} 
              />
            </section>

            {selectedItem && (
              <section className="pt-4 border-t border-slate-200">
                <NavigatorDetail item={selectedItem} />
              </section>
            )}
          </div>
        ) : (
          <div className="p-8 space-y-8">
            <div className="text-center space-y-4">
              <div className="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mx-auto text-slate-300">
                <Search className="w-6 h-6" />
              </div>
              <p className="text-sm text-slate-500 font-medium">
                No navigational matches found.
              </p>
            </div>

            <section className="space-y-4">
              <h3 className="text-[10px] font-black text-slate-400 uppercase tracking-widest px-2">Popular Actions</h3>
              <div className="grid gap-2">
                {[
                  { title: "Scholarships", desc: "Find government and private funds" },
                  { title: "Exam Registration", desc: "Deadlines and application links" },
                  { title: "Re-evaluation", desc: "Process for marks correction" }
                ].map((action, idx) => (
                  <button 
                    key={idx} 
                    className="w-full text-left p-4 bg-white hover:bg-blue-50/50 border border-slate-100 rounded-xl transition-all group"
                  >
                    <div className="flex justify-between items-start">
                      <div>
                        <p className="text-sm font-bold text-slate-700 group-hover:text-blue-600">{action.title}</p>
                        <p className="text-xs text-slate-500 mt-1">{action.desc}</p>
                      </div>
                      <Star className="w-3.5 h-3.5 text-slate-200 group-hover:text-amber-400 group-hover:fill-amber-400 transition-colors" />
                    </div>
                  </button>
                ))}
              </div>
            </section>
          </div>
        )}
      </div>
    </div>
  )
}
