import { useEffect, useState } from 'react';
import { api } from '../../api/client';
import { formatDate } from '../../lib/format';
import type { Order } from './types';

type OrderDetailsPageProps = {
  orderId: string;
};

export function OrderDetailsPage({ orderId }: OrderDetailsPageProps) {
  const [order, setOrder] = useState<Order | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    api
      .get<Order>(`/orders/${orderId}`)
      .then(setOrder)
      .catch((err: Error) => setError(err.message));
  }, [orderId]);

  if (error) {
    return <p className="error">{error}</p>;
  }

  if (!order) {
    return <p>Loading…</p>;
  }

  return (
    <article>
      <h1>Order {order.id}</h1>
      <p>
        {order.customerName} · placed {formatDate(order.createdAt)}
      </p>
    </article>
  );
}
