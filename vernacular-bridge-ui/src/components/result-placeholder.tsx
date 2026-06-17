import React from 'react';
import { Sparkles } from 'lucide-react';

export default function ResultPlaceholder() {
  return (
    <div className="bg-white rounded-2xl border-2 border-dashed border-gray-200 h-full flex flex-col items-center justify-center p-12 text-center text-gray-400">
      <div className="bg-gray-50 p-6 rounded-full mb-6">
        <Sparkles className="w-12 h-12 text-gray-300" />
      </div>
      <h3 className="text-xl font-semibold text-gray-500 mb-2">Ready to Transform</h3>
      <p className="max-w-xs">
        Enter a concept on the left to see the cognitive transformation in action.
      </p>
    </div>
  );
}
