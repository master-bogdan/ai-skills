export const ORDER_STATUS = {
  PENDING: 'pending',
  PAID: 'paid',
  SHIPPED: 'shipped',
  CANCELLED: 'cancelled',
} as const;

export type OrderStatus = (typeof ORDER_STATUS)[keyof typeof ORDER_STATUS];

export type LineItem = {
  id: string;
  name: string;
  quantity: number;
  unitPriceCents: number;
};

export type Refund = {
  id: string;
  amountCents: number;
  reason: string;
  createdAt: string;
};

export type Order = {
  id: string;
  customerName: string;
  customerEmail: string;
  status: OrderStatus;
  createdAt: string;
  dueAt: string;
  chargeId: string;
  lineItems: LineItem[];
  discountCents: number;
  taxCents: number;
  totalCents: number;
  refunds: Refund[];
};
