import { ReactNode } from 'react';
import { FileText } from 'lucide-react';

interface AuthLayoutProps {
  title: string;
  subtitle: string;
  footer: ReactNode;
  children: ReactNode;
}

export function AuthLayout({ title, subtitle, footer, children }: AuthLayoutProps) {
  return (
    <main className="min-h-screen flex flex-col items-center justify-center bg-gray-50 px-4 py-12">
      <div className="mb-8 flex flex-col items-center text-center">
        <div className="flex items-center gap-2.5">
          <span className="flex h-10 w-10 items-center justify-center rounded-lg bg-blue-600 text-white">
            <FileText className="h-5 w-5" />
          </span>
          <span className="text-2xl font-bold tracking-tight text-gray-900">Proposal SaaS</span>
        </div>
        <p className="mt-3 max-w-sm text-sm text-gray-500">
          Create professional commercial proposals, calculate taxes automatically, and export them as PDF.
        </p>
      </div>

      <div className="w-full max-w-md rounded-xl border border-gray-200 bg-white p-8 shadow-sm">
        <h1 className="text-xl font-semibold text-gray-900">{title}</h1>
        <p className="mt-1 mb-6 text-sm text-gray-500">{subtitle}</p>

        {children}

        <p className="mt-6 text-center text-sm text-gray-600">{footer}</p>
      </div>
    </main>
  );
}
