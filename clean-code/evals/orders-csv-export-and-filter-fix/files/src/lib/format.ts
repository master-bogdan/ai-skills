const currencyFormatters = new Map<string, Intl.NumberFormat>();

export const formatCurrency = (amountCents: number, currency = 'USD'): string => {
  if (!currencyFormatters.has(currency)) {
    currencyFormatters.set(currency, new Intl.NumberFormat('en-US', { style: 'currency', currency }));
  }

  return currencyFormatters.get(currency)!.format(amountCents / 100);
};

export const formatDate = (isoDate: string): string =>
  new Date(isoDate).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
