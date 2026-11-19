'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useForm, useFieldArray } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import axios from 'axios';
import { Plus, Trash2, ArrowLeft } from 'lucide-react';
import { api } from '@/lib/api';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';

const proposalSchema = z.object({
  title: z.string().min(3, 'Title must be at least 3 characters'),
  description: z.string().optional(),
  tax_rate: z.number().min(0).max(100),
  items: z
    .array(
      z.object({
        description: z.string().min(1, 'Description is required'),
        quantity: z.number().min(1, 'Min quantity is 1'),
        unit_price: z.number().min(0, 'Price must be positive'),
      })
    )
    .min(1, 'At least one item is required'),
});

type ProposalFormValues = z.infer<typeof proposalSchema>;

function getErrorMessage(error: unknown): string {
  if (axios.isAxiosError(error)) {
    if (!error.response) {
      return 'Unable to reach the server. It may be waking up, please try again in a minute.';
    }
    const detail = error.response.data?.detail ?? error.response.data?.error;
    const message = typeof detail === 'string' ? detail : JSON.stringify(detail);
    return `Request failed (${error.response.status})${message ? `: ${message}` : ''}`;
  }
  return 'Something went wrong while creating the proposal.';
}

export default function ProposalForm() {
  const router = useRouter();
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const {
    register,
    control,
    handleSubmit,
    formState: { errors },
  } = useForm<ProposalFormValues>({
    resolver: zodResolver(proposalSchema),
    defaultValues: {
      tax_rate: 0,
      items: [{ description: '', quantity: 1, unit_price: 0 }],
    },
  });

  const { fields, append, remove } = useFieldArray({
    control,
    name: 'items',
  });

  const onSubmit = async (data: ProposalFormValues) => {
    setIsSubmitting(true);
    setSubmitError('');

    try {
      await api.post('/proposals/', { ...data, client_id: 1 });
      router.push('/');
      router.refresh();
    } catch (error) {
      if (axios.isAxiosError(error) && error.response?.status === 401) {
        localStorage.removeItem('token');
        router.push('/login');
        return;
      }
      console.error('Failed to create proposal', error);
      setSubmitError(getErrorMessage(error));
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-3xl mx-auto p-6">
      <header className="mb-8 flex items-center gap-4">
        <Link href="/" className="text-gray-500 hover:text-gray-900 transition-colors">
          <ArrowLeft className="w-6 h-6" />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">New Proposal</h1>
          <p className="text-gray-500 text-sm mt-1">Create a new commercial proposal for your client.</p>
        </div>
      </header>

      <form
        onSubmit={handleSubmit(onSubmit)}
        className="space-y-6 bg-white p-6 rounded-xl shadow-sm border border-gray-200"
      >
        {submitError && (
          <div role="alert" className="p-3 bg-red-50 text-red-600 rounded-md text-sm">
            {submitError}
          </div>
        )}

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          <Input
            label="Proposal Title"
            placeholder="e.g. Website Redesign"
            {...register('title')}
            error={errors.title?.message}
          />
          <Input
            label="Tax Rate (%)"
            type="number"
            step="0.01"
            {...register('tax_rate', { valueAsNumber: true })}
            error={errors.tax_rate?.message}
          />
        </div>

        <div>
          <label className="text-sm font-medium text-gray-700 mb-2 block">Line Items</label>
          <div className="space-y-4">
            {fields.map((field, index) => (
              <div
                key={field.id}
                className="flex gap-4 items-start p-4 bg-gray-50 rounded-lg border border-gray-100"
              >
                <div className="flex-1">
                  <Input
                    placeholder="Item description"
                    {...register(`items.${index}.description`)}
                    error={errors.items?.[index]?.description?.message}
                  />
                </div>
                <div className="w-24">
                  <Input
                    type="number"
                    placeholder="Qty"
                    {...register(`items.${index}.quantity`, { valueAsNumber: true })}
                    error={errors.items?.[index]?.quantity?.message}
                  />
                </div>
                <div className="w-32">
                  <Input
                    type="number"
                    step="0.01"
                    placeholder="Unit Price"
                    {...register(`items.${index}.unit_price`, { valueAsNumber: true })}
                    error={errors.items?.[index]?.unit_price?.message}
                  />
                </div>
                <button
                  type="button"
                  onClick={() => remove(index)}
                  className="mt-2 text-gray-400 hover:text-red-500 transition-colors"
                  disabled={fields.length === 1}
                >
                  <Trash2 className="w-5 h-5" />
                </button>
              </div>
            ))}
          </div>
          <Button
            type="button"
            variant="secondary"
            className="mt-4"
            onClick={() => append({ description: '', quantity: 1, unit_price: 0 })}
          >
            <Plus className="w-4 h-4 mr-2" />
            Add Item
          </Button>
        </div>

        <div className="pt-6 border-t border-gray-100 flex justify-end gap-4">
          <Link href="/">
            <Button type="button" variant="secondary">Cancel</Button>
          </Link>
          <Button type="submit" isLoading={isSubmitting}>
            Create Proposal
          </Button>
        </div>
      </form>
    </div>
  );
}
