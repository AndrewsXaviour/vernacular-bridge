"use client";

import React, { useState } from 'react';
import HeroSection from '@/components/home/hero-section';
import FeatureCards from '@/components/home/feature-cards';
import HomeFooter from '@/components/home/home-footer';
import { useRouter } from 'next/navigation';

export default function Home() {
  const router = useRouter();

  const handleHomeSubmit = (text: string) => {
    // Simple redirect to learn page with the query
    router.push(`/learn?q=${encodeURIComponent(text)}`);
  };

  return (
    <div className="flex-1 bg-[#f8f9fc] flex flex-col font-sans overflow-x-hidden">
      <div className="flex-1 w-full bg-white flex flex-col">
         <HeroSection />
         <FeatureCards />
         <div className="bg-[#f8f9fc] border-t border-slate-100 flex-grow pt-4">
           <HomeFooter onTransform={handleHomeSubmit} isLoading={false} />
         </div>
      </div>
    </div>
  );
}
