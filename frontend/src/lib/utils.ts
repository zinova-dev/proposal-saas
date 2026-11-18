/**
 * Formats a number to US Dollar currency.
 * Enforced for the American market standard.
 */
export function formatCurrency(value: number) {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
  }).format(value);
}
