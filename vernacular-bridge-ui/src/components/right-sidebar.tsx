import React from 'react';
import { Bookmark, Lightbulb, Link as LinkIcon, ChevronRight } from 'lucide-react';

export default function RightSidebar() {
  return (
    <aside className="w-[320px] h-[calc(100vh-4rem)] bg-white border-l border-slate-200 p-6 font-sans overflow-y-auto fixed top-16 right-0">
      
      {/* Concept Snapshot */}
      <div className="mb-6 p-5 border border-green-100 rounded-2xl bg-white shadow-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Bookmark className="w-4 h-4 text-green-600" />
          <h3 className="text-sm font-bold text-slate-800">Concept Snapshot</h3>
        </div>
        <div className="space-y-3">
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">Topic</span>
            <span className="font-semibold text-slate-800">Biology</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">Subtopic</span>
            <span className="font-semibold text-slate-800">Photosynthesis</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">Difficulty</span>
            <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">Easy</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">Exam Relevance</span>
            <span className="bg-green-100 text-green-700 px-2 py-0.5 rounded-full font-bold">High</span>
          </div>
          <div className="flex justify-between items-center text-xs">
            <span className="text-slate-500 font-medium">Mapped To</span>
            <span className="font-semibold text-slate-800">11th Std - Botany</span>
          </div>
        </div>
      </div>

      {/* Key Takeaways */}
      <div className="mb-6 p-5 border border-slate-200 rounded-2xl bg-white shadow-sm">
        <div className="flex items-center space-x-2 mb-4">
          <Lightbulb className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-bold text-slate-800">Key Takeaways</h3>
        </div>
        <ul className="space-y-2 text-xs font-medium text-slate-700">
          <li className="flex items-start space-x-2">
            <span className="text-blue-500 font-bold mt-0.5">✓</span>
            <span>Plants make their own food.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-500 font-bold mt-0.5">✓</span>
            <span>Sunlight is the energy source.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-500 font-bold mt-0.5">✓</span>
            <span>CO₂ + H₂O &rarr; Glucose + O₂</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-500 font-bold mt-0.5">✓</span>
            <span>Chlorophyll is the key pigment.</span>
          </li>
          <li className="flex items-start space-x-2">
            <span className="text-blue-500 font-bold mt-0.5">✓</span>
            <span>Oxygen is released as a by-product.</span>
          </li>
        </ul>
      </div>

      {/* Related Concepts */}
      <div className="mb-6 p-5 border border-slate-200 rounded-2xl bg-white shadow-sm">
        <div className="flex items-center space-x-2 mb-4">
          <LinkIcon className="w-4 h-4 text-blue-500" />
          <h3 className="text-sm font-bold text-slate-800">Related Concepts</h3>
        </div>
        <ul className="space-y-3">
          {['Respiration in Plants', 'Transpiration', 'Carbon Cycle', 'Cell Structure (Chloroplast)'].map((concept, idx) => (
            <li key={idx}>
              <a href="#" className="flex justify-between items-center text-xs font-medium text-blue-600 hover:text-blue-800 group">
                <span>{concept}</span>
                <ChevronRight className="w-3.5 h-3.5 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-0.5 transition-transform" />
              </a>
            </li>
          ))}
        </ul>
      </div>

      {/* Still Confused */}
      <div className="p-5 bg-orange-50 border border-orange-100 rounded-2xl shadow-sm">
        <h3 className="text-sm font-bold text-orange-900 mb-2">Still confused?</h3>
        <p className="text-xs text-orange-800 font-medium mb-4 leading-relaxed">
          Ask a follow-up or go to Writing Coach to test your understanding.
        </p>
        <div className="flex space-x-2">
          <button className="flex-1 bg-white text-blue-600 border border-blue-200 hover:bg-blue-50 font-bold text-xs py-2 rounded-lg transition-colors">
            Ask Follow-up
          </button>
          <button className="flex-1 bg-blue-600 text-white hover:bg-blue-700 font-bold text-xs py-2 rounded-lg transition-colors shadow-sm shadow-blue-600/20">
            Go to Coach
          </button>
        </div>
      </div>
      
      <div className="h-8" />
    </aside>
  );
}
