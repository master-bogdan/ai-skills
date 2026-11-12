import { useState } from 'react';
import { Badge } from '../../components/ui/badge';
import { Button } from '../../components/ui/button';
import { formatCurrency, formatDate } from '../../lib/format';
import { ORDER_STATUS, type Order } from './types';

type StatusFilter = 'all' | 'active';

type OrderListProps = {
  orders: Order[];
  onOpen: (orderId: string) => void;
};

export function OrderList({ orders, onOpen }: OrderListProps) {
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');

  const visibleOrders =
    statusFilter === 'active'
      ? orders.filter((order) => order.status !== ORDER_STATUS.SHIPPED)
      : orders;

  if (orders.length === 0) {
    return <p className="empty">No orders yet.</p>;
  }

  return (
    <section>
      <div className="toolbar">
        <Button variant="secondary" onClick={() => setStatusFilter('all')}>
          All
        </Button>
        <Button variant="secondary" onClick={() => setStatusFilter('active')}>
          Active
        </Button>
      </div>
      <table>
        <thead>
          <tr>
            <th>Order</th>
            <th>Customer</th>
            <th>Total</th>
            <th>Status</th>
            <th>Created</th>
          </tr>
        </thead>
        <tbody>
          {visibleOrders.map((order) => (
            <tr key={order.id} onClick={() => onOpen(order.id)}>
              <td>{order.id}</td>
              <td>{order.customerName}</td>
              <td>{formatCurrency(order.totalCents)}</td>
              <td>
                <Badge>{order.status}</Badge>
              </td>
              <td>{formatDate(order.createdAt)}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </section>
  );
}
