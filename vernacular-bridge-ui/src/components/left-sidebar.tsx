'use client';

import React from 'react';
import { BookOpen, PenTool, Target, Map, TrendingUp, HelpCircle, ArrowRight } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

export default function LeftSidebar() {
  const pathname = usePathname();

  const menuItems = [
    {
      title: 'Concept Bridge',
      subtitle: 'Learn & Understand',
      icon: <BookOpen className="w-5 h-5" />,
      href: '/learn',
    },
    {
      title: 'Writing Coach',
      subtitle: 'Improve Answers',
      icon: <PenTool className="w-5 h-5" />,
      href: '/coach',
    },
    {
      title: 'Practice',
      subtitle: 'MCQs & Drills',
      icon: <Target className="w-5 h-5" />,
      href: '/practice',
    },
    {
      title: 'Navigator',
      subtitle: 'Schemes & Processes',
      icon: <Map className="w-5 h-5" />,
      href: '/navigator',
    },
    {
      title: 'Progress',
      subtitle: 'My Learning Dashboard',
      icon: <TrendingUp className="w-5 h-5" />,
      href: '/progress',
    }
  ];

  return (
    <aside className="w-[280px] h-[calc(100vh-4rem)] bg-slate-50 border-r border-slate-200 flex flex-col p-4 font-sans fixed top-16 left-0">
      <nav className="flex-1 space-y-2 mt-4">
        {menuItems.map((item, idx) => {
          const isActive = pathname === item.href || (pathname?.startsWith(item.href) && item.href !== '/');
          return (
            <Link
              key={idx}
              href={item.href}
              className={`flex items-start space-x-3 p-3 rounded-xl transition-all ${
                isActive 
                  ? 'bg-blue-50 text-blue-700 shadow-sm border border-blue-100' 
                  : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900 border border-transparent'
              }`}
            >
              <div className={`mt-0.5 ${isActive ? 'text-blue-600' : 'text-slate-400'}`}>
                {item.icon}
              </div>
              <div className="flex flex-col">
                <span className={`text-sm font-bold ${isActive ? 'text-blue-700' : 'text-slate-700'}`}>
                  {item.title}
                </span>
                <span className={`text-[11px] font-medium ${isActive ? 'text-blue-500' : 'text-slate-400'}`}>
                  {item.subtitle}
                </span>
              </div>
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto">
        <Link href="/help" className="flex items-center justify-between p-4 bg-white border border-slate-200 rounded-xl hover:shadow-md transition-shadow group">
          <div className="flex items-center space-x-3">
            <div className="p-1.5 bg-slate-100 rounded-lg text-slate-500 group-hover:text-blue-600 group-hover:bg-blue-50 transition-colors">
              <HelpCircle className="w-4 h-4" />
            </div>
            <div className="flex flex-col">
              <span className="text-sm font-bold text-slate-800">Need help?</span>
              <span className="text-[11px] font-medium text-slate-500">See how it works</span>
            </div>
          </div>
          <ArrowRight className="w-4 h-4 text-slate-400 group-hover:text-blue-600 group-hover:translate-x-1 transition-all" />
        </Link>
      </div>
    </aside>
  );
}
