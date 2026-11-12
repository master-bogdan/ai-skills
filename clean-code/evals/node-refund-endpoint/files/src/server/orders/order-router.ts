import { Router } from 'express';
import { orderController } from './order-controller';

export const orderRouter = Router();

orderRouter.get('/:id', orderController.getById);
orderRouter.post('/:id/cancel', orderController.cancel);
