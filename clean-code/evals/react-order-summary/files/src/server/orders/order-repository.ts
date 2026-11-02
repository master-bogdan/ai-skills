import type { Order, Refund } from '../../features/orders/types';
import { db } from '../db';

export const orderRepository = {
  findById: async (orderId: string): Promise<Order | null> =>
    db.one<Order>('SELECT * FROM orders WHERE id = $1', [orderId]),

  updateStatus: async (orderId: string, status: Order['status']): Promise<void> => {
    await db.none('UPDATE orders SET status = $2 WHERE id = $1', [orderId, status]);
  },

  addRefund: async (orderId: string, refund: Refund): Promise<void> => {
    await db.none('INSERT INTO refunds (id, order_id, amount_cents, reason, created_at) VALUES ($1, $2, $3, $4, $5)', [
      refund.id,
      orderId,
      refund.amountCents,
      refund.reason,
      refund.createdAt,
    ]);
  },
};
