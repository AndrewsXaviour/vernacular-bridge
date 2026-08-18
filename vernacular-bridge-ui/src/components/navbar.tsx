'use client';

import React from 'react';
import { Moon, ChevronDown, User } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavbarProps {
  isLoggedIn?: boolean;
}

export default function Navbar({ isLoggedIn = false }: NavbarProps) {
  const pathname = usePathname();
  
  const navLinks = [
    { name: 'Home', href: '/' },
    { name: 'Learn', href: '/learn' },
    { name: 'Coach', href: '/coach' },
    { name: 'Practice', href: '/practice' },
    { name: 'Navigator', href: '/navigator' },
    { name: 'Progress', href: '/progress' },
  ];

  return (
    <nav className="bg-white border-b border-gray-200 sticky top-0 z-50 h-16 flex items-center px-6 font-sans">
      <div className="flex items-center space-x-3 w-1/4">
        {/* Mock Bridge Logo */}
        <Link href="/" className="text-blue-600 flex items-center space-x-3 group">
          <svg width="32" height="24" viewBox="0 0 32 24" fill="currentColor" className="group-hover:scale-105 transition-transform">
            <path d="M4 22L4 8L16 2L28 8L28 22H24L24 14H8L8 22H4ZM2 24H10V16H22V24H30V7L16 0L2 7V24Z"/>
          </svg>
          <div className="flex flex-col">
            <span className="text-lg font-bold text-slate-900 leading-tight">
              Vernacular Bridge
            </span>
            <span className="text-[10px] text-slate-500 font-medium">
              Tamil understanding &rarr; Academic English
            </span>
          </div>
        </Link>
      </div>

      <div className="flex-1 flex justify-center h-full">
        <ul className="flex space-x-8 h-full">
          {navLinks.map((link) => {
            const isActive = pathname === link.href || (pathname?.startsWith(link.href) && link.href !== '/');
            return (
              <li key={link.name} className="h-full flex items-center">
                <Link 
                  href={link.href} 
                  className={`text-sm font-medium h-full flex items-center px-1 border-b-2 transition-colors ${
                    isActive 
                      ? 'border-blue-600 text-blue-600' 
                      : 'border-transparent text-slate-600 hover:text-slate-900 hover:border-slate-300'
                  }`}
                >
                  {link.name}
                </Link>
              </li>
            );
          })}
        </ul>
      </div>

      <div className="flex items-center justify-end space-x-4 w-1/4">
        <button className="text-sm font-medium text-slate-700 hover:bg-slate-50 px-3 py-1.5 rounded-full border border-slate-200">
          தமிழ் / EN
        </button>
        <button className="p-2 text-slate-500 hover:bg-slate-50 rounded-full border border-transparent hover:border-slate-200">
          <Moon className="w-4 h-4" />
        </button>
        <div className="flex items-center pl-2 border-l border-slate-200">
          {isLoggedIn ? (
            <div className="flex items-center space-x-2 cursor-pointer">
              <div className="w-8 h-8 rounded-full bg-slate-700 text-white flex items-center justify-center text-xs font-bold">
                S
              </div>
              <span className="text-sm font-medium text-slate-700">Student</span>
              <ChevronDown className="w-4 h-4 text-slate-400" />
            </div>
          ) : (
            <button className="flex items-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-bold text-sm transition-colors shadow-sm">
              <User className="w-4 h-4" />
              <span>Sign In</span>
            </button>
          )}
        </div>
      </div>
    </nav>
  );
}
