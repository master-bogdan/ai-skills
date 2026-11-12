import type { Request, Response } from 'express';
import { getAuthUser } from '../http/auth';
import { orderService } from './order-service';

export const orderController = {
  getById: async (req: Request, res: Response) => {
    const order = await orderService.getById(req.params.id);
    res.json(order);
  },

  cancel: async (req: Request, res: Response) => {
    const order = await orderService.cancel(req.params.id, getAuthUser(req));
    res.json(order);
  },
};
