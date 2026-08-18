import React from 'react';
import LeftSidebar from '@/components/left-sidebar';
import RightSidebar from '@/components/right-sidebar';

export default function WorkspaceLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex flex-1 relative max-w-[1600px] mx-auto w-full">
      <LeftSidebar />
      <main className="flex-1 lg:ml-[280px] lg:mr-[320px] p-6 pb-24 h-[calc(100vh-4rem)] overflow-y-auto w-full">
        {children}
      </main>
      <div className="hidden lg:block">
        <RightSidebar />
      </div>
    </div>
  );
}
