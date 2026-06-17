import React from 'react';
import { ShieldCheck } from 'lucide-react';

export default function Navbar() {
  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between items-center h-16">
          <div className="flex flex-col">
            <span className="text-2xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-[#0f766e] to-[#1e40af]">
              Vernacular Bridge
            </span>
            <span className="text-xs text-gray-500 font-medium">
              From Tamil Understanding to Academic Excellence
            </span>
          </div>
          <div className="flex items-center space-x-2">
            <div className="flex items-center bg-teal-50 px-3 py-1 rounded-full border border-teal-100">
              <ShieldCheck className="w-4 h-4 text-[#0f766e] mr-1.5" />
              <span className="text-xs font-semibold text-[#0f766e]">
                Fully Offline • Zero Cost
              </span>
            </div>
          </div>
        </div>
      </div>
    </nav>
  );
}
