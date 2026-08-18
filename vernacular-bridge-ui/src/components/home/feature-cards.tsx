import React from 'react';
import { BookOpen, PenTool, Target, Map, TrendingUp, ArrowRight } from 'lucide-react';
import Link from 'next/link';

export default function FeatureCards() {
  const features = [
    {
      title: 'Concept Bridge (Learn)',
      desc: 'Understand any concept in Tamil, with clear Academic English, steps, and examples.',
      icon: <BookOpen className="w-5 h-5" />,
      color: 'green',
      href: '/learn'
    },
    {
      title: 'Writing Coach',
      desc: 'Paste your answer and get structured feedback, score (0-10), and improvement tips.',
      icon: <PenTool className="w-5 h-5" />,
      color: 'purple',
      href: '/coach'
    },
    {
      title: 'Practice & Exam Prep',
      desc: 'MCQs, misconceptions, and application questions to strengthen your concepts.',
      icon: <Target className="w-5 h-5" />,
      color: 'orange',
      href: '/practice'
    },
    {
      title: 'Navigator',
      desc: 'Explore government schemes and processes with simple bilingual explanations.',
      icon: <Map className="w-5 h-5" />,
      color: 'teal',
      href: '/navigator'
    },
    {
      title: 'My Progress',
      desc: 'Track your learning, coach scores, weak areas, and mastery over time.',
      icon: <TrendingUp className="w-5 h-5" />,
      color: 'blue',
      href: '/progress'
    }
  ];

  const getColorClasses = (color: string) => {
    switch (color) {
      case 'green': return 'border-green-100 text-green-700 bg-green-50/50 hover:border-green-300';
      case 'purple': return 'border-purple-100 text-purple-700 bg-purple-50/50 hover:border-purple-300';
      case 'orange': return 'border-orange-100 text-orange-700 bg-orange-50/50 hover:border-orange-300';
      case 'teal': return 'border-teal-100 text-teal-700 bg-teal-50/50 hover:border-teal-300';
      case 'blue': return 'border-blue-100 text-blue-700 bg-blue-50/50 hover:border-blue-300';
      default: return 'border-slate-100 text-slate-700 bg-slate-50/50 hover:border-slate-300';
    }
  };

  const getIconContainerClasses = (color: string) => {
    switch (color) {
      case 'green': return 'bg-green-100 text-green-600';
      case 'purple': return 'bg-purple-100 text-purple-600';
      case 'orange': return 'bg-orange-100 text-orange-600';
      case 'teal': return 'bg-teal-100 text-teal-600';
      case 'blue': return 'bg-blue-100 text-blue-600';
      default: return 'bg-slate-100 text-slate-600';
    }
  };

  return (
    <div className="w-full max-w-7xl mx-auto px-6 py-8 font-sans">
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-5 gap-4">
        {features.map((feature, idx) => (
          <Link 
            key={idx} 
            href={feature.href}
            className={`flex flex-col p-5 rounded-2xl border bg-white shadow-sm transition-all duration-300 group cursor-pointer hover:shadow-md ${getColorClasses(feature.color).split(' ')[0]} ${getColorClasses(feature.color).split(' ').pop()}`}
          >
            <div className={`w-10 h-10 rounded-full flex items-center justify-center mb-4 ${getIconContainerClasses(feature.color)}`}>
              {feature.icon}
            </div>
            <h3 className="text-xs font-bold text-slate-900 mb-2 leading-tight">
              {feature.title}
            </h3>
            <p className="text-[10px] text-slate-600 font-medium leading-relaxed flex-grow">
              {feature.desc}
            </p>
            <div className="mt-4 flex justify-end">
              <ArrowRight className={`w-4 h-4 transition-transform group-hover:translate-x-1 ${getColorClasses(feature.color).split(' ')[1]}`} />
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
