'use client';

import dynamic from 'next/dynamic';

// Dynamically import the form and disable SSR to prevent UUID hydration errors
const ProposalForm = dynamic(() => import('./ProposalForm'), {
  ssr: false,
  loading: () => (
    <div className="max-w-3xl mx-auto p-6 flex justify-center items-center h-64">
      <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
    </div>
  ),
});

export default function NewProposalPage() {
  return <ProposalForm />;
}
