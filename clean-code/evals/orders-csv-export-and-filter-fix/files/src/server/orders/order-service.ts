import { ORDER_STATUS, type Order } from '../../features/orders/types';
import { ForbiddenError, NotFoundError, ValidationError } from '../errors';
import type { AuthUser } from '../http/auth';
import { orderRepository } from './order-repository';

const getOrderOrThrow = async (orderId: string): Promise<Order> => {
  const order = await orderRepository.findById(orderId);

  if (!order) {
    throw new NotFoundError('Order', orderId);
  }

  return order;
};

export const orderService = {
  getById: getOrderOrThrow,

  cancel: async (orderId: string, user: AuthUser): Promise<Order> => {
    if (user.role === 'customer') {
      throw new ForbiddenError('Customers cannot cancel orders');
    }

    const order = await getOrderOrThrow(orderId);

    if (order.status === ORDER_STATUS.SHIPPED) {
      throw new ValidationError('Shipped orders cannot be cancelled');
    }

    await orderRepository.updateStatus(orderId, ORDER_STATUS.CANCELLED);
    return { ...order, status: ORDER_STATUS.CANCELLED };
  },
};
