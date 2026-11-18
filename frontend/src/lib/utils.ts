/**
 * Formats a number to a currency string.
 * Defaults to USD for international clients.
 */
export function formatCurrency(value: number, currency: string = 'USD') {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: currency,
  }).format(value);
}
