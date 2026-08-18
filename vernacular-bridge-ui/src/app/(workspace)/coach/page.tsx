import React, { Suspense } from 'react';
import CoachWorkspaceClient from '@/components/coach/CoachWorkspaceClient';

export default function CoachWorkspace() {
  return (
    <Suspense fallback={<div className="p-12 text-center text-slate-500">Loading Coach Workspace...</div>}>
      <CoachWorkspaceClient />
    </Suspense>
  )
}
