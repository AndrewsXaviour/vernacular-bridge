import React from 'react';
import { GraduationCap, Sparkles, PlayCircle, MessageSquare, ShieldCheck, Lock } from 'lucide-react';
import Link from 'next/link';
import Image from 'next/image';

export default function HeroSection() {
  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-16 md:py-24 flex flex-col md:flex-row items-center justify-between font-sans relative gap-12">
      
      {/* Left Column - Copy */}
      <div className="w-full md:w-1/2 flex flex-col space-y-6 z-10">
        
        <div className="inline-flex items-center space-x-2 bg-green-50 text-green-700 px-3 py-1.5 rounded-full border border-green-100 self-start">
          <GraduationCap className="w-4 h-4" />
          <span className="text-xs font-bold tracking-wide">Built for First-Generation College Students</span>
        </div>
        
        <h1 className="text-5xl md:text-[4rem] font-black text-slate-900 tracking-tight leading-[1.05]">
          Understand in <span className="text-green-600">Tamil.</span><br />
          Excel in <span className="text-blue-600">English.</span>
        </h1>
        
        <p className="text-slate-600 font-medium text-lg leading-relaxed max-w-xl">
          Bridging the language-knowledge gap for government university students with AI-powered concept explanations, exam prep, and writing coaching.
        </p>
        
        <div className="flex flex-col sm:flex-row items-start sm:items-center space-y-3 sm:space-y-0 sm:space-x-4 pt-2">
          <Link href="/learn" className="bg-blue-600 text-white px-6 py-3 rounded-xl font-bold flex items-center space-x-2 hover:bg-blue-700 transition-colors shadow-sm shadow-blue-600/20">
            <Sparkles className="w-4 h-4" />
            <span>Try a concept now</span>
          </Link>
          <Link href="/help" className="bg-white text-slate-700 border border-slate-200 px-6 py-3 rounded-xl font-bold flex items-center space-x-2 hover:bg-slate-50 transition-colors shadow-sm">
            <PlayCircle className="w-4 h-4" />
            <span>See how it works</span>
          </Link>
        </div>
        
        <div className="flex flex-wrap items-center gap-6 pt-6">
          <div className="flex items-center space-x-2">
             <div className="p-1.5 bg-green-50 rounded-full text-green-600">
               <MessageSquare className="w-4 h-4" />
             </div>
             <div className="flex flex-col">
               <span className="text-xs font-bold text-slate-700 leading-tight">Bilingual AI</span>
               <span className="text-[10px] font-medium text-slate-500">(Tamil + English)</span>
             </div>
          </div>
          <div className="flex items-center space-x-2">
             <div className="p-1.5 bg-green-50 rounded-full text-green-600">
               <ShieldCheck className="w-4 h-4" />
             </div>
             <div className="flex flex-col">
               <span className="text-xs font-bold text-slate-700 leading-tight">Fact-Locked</span>
               <span className="text-[10px] font-medium text-slate-500">Explanations</span>
             </div>
          </div>
          <div className="flex items-center space-x-2">
             <div className="p-1.5 bg-blue-50 rounded-full text-blue-600">
               <Lock className="w-4 h-4" />
             </div>
             <div className="flex flex-col">
               <span className="text-xs font-bold text-slate-700 leading-tight">Privacy</span>
               <span className="text-[10px] font-medium text-slate-500">First</span>
             </div>
          </div>
        </div>
      </div>

      {/* Right Column - Bridge Graphic Representation */}
      <div className="w-full md:w-1/2 mt-16 md:mt-0 relative flex items-center justify-center">
         <Image 
           src="/bridge-graphic.png" 
           alt="Tamil to English Bridge"
           width={800}
           height={600}
           className="w-full h-auto max-w-lg object-contain drop-shadow-sm pointer-events-none"
         />
      </div>
    </div>
  );
}
