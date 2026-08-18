
export default function PlaceholderPage() {
  return (
    <div className="flex flex-col items-center justify-center h-full text-center space-y-4 pt-32">
      <div className="w-16 h-16 bg-blue-50 text-blue-600 rounded-full flex items-center justify-center mb-2">
        <svg className="w-8 h-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      </div>
      <h1 className="text-2xl font-bold text-slate-900">Coming Soon</h1>
      <p className="text-slate-500 max-w-sm">This workspace is currently under development. Check back later!</p>
    </div>
  );
}
