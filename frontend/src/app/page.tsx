'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';
import { api } from '@/lib/api';
import { formatCurrency } from '@/lib/utils';
import { Button } from '@/components/ui/Button';
import { Plus, FileText, CheckCircle2, Clock, Download } from 'lucide-react';

interface Proposal {
  id: number;
  title: string;
  status: string;
  subtotal: number;
  total: number;
  created_at: string;
}

export default function Dashboard() {
  const [proposals, setProposals] = useState<Proposal[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    async function fetchProposals() {
      try {
        const response = await api.get('/proposals/');
        setProposals(response.data);
      } catch (error) {
        console.error('Failed to fetch proposals:', error);
      } finally {
        setIsLoading(false);
      }
    }
    fetchProposals();
  }, []);

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'ACCEPTED': return <CheckCircle2 className="w-4 h-4 text-green-500" />;
      case 'SENT': return <Clock className="w-4 h-4 text-blue-500" />;
      default: return <FileText className="w-4 h-4 text-gray-500" />;
    }
  };

  const handleDownloadPdf = (id: number) => {
    const baseUrl = process.env.NEXT_PUBLIC_API_URL;
    window.open(`${baseUrl}/proposals/${id}/pdf`, '_blank');
  };

  return (
    <div className="max-w-6xl mx-auto p-6">
      <header className="flex justify-between items-center mb-8">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Proposals</h1>
          <p className="text-gray-500 text-sm mt-1">Manage your commercial proposals and track their status.</p>
        </div>
        <Link href="/proposals/new">
          <Button>
            <Plus className="w-4 h-4 mr-2" />
            New Proposal
          </Button>
        </Link>
      </header>

      <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
        {isLoading ? (
          <div className="p-8 text-center text-gray-500">Loading proposals...</div>
        ) : proposals.length === 0 ? (
          <div className="p-12 text-center flex flex-col items-center">
            <FileText className="w-12 h-12 text-gray-300 mb-4" />
            <h3 className="text-lg font-medium text-gray-900">No proposals yet</h3>
            <p className="text-gray-500 mt-1">Get started by creating your first commercial proposal.</p>
          </div>
        ) : (
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-gray-50 border-b border-gray-200 text-xs uppercase text-gray-500 font-semibold">
                <th className="px-6 py-3">Title</th>
                <th className="px-6 py-3">Status</th>
                <th className="px-6 py-3">Date</th>
                <th className="px-6 py-3 text-right">Total</th>
                <th className="px-6 py-3 text-center">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {proposals.map((proposal) => (
                <tr key={proposal.id} className="hover:bg-gray-50 transition-colors">
                  <td className="px-6 py-4 font-medium text-gray-900">{proposal.title}</td>
                  <td className="px-6 py-4 flex items-center gap-2 text-sm text-gray-600">
                    {getStatusIcon(proposal.status)}
                    {proposal.status}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(proposal.created_at).toLocaleDateString('en-US')}
                  </td>
                  <td className="px-6 py-4 text-right font-medium text-gray-900">
                    {formatCurrency(proposal.total)}
                  </td>
                  <td className="px-6 py-4 text-center">
                    <button
                      onClick={() => handleDownloadPdf(proposal.id)}
                      className="text-blue-600 hover:text-blue-800 transition-colors p-2 rounded-full hover:bg-blue-50"
                      title="Download PDF"
                    >
                      <Download className="w-5 h-5" />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
