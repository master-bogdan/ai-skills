import type { Request } from 'express';
import { ForbiddenError } from '../errors';

export type AuthUser = {
  id: string;
  role: 'admin' | 'staff' | 'customer';
};

export const getAuthUser = (req: Request): AuthUser => {
  const user = (req as Request & { user?: AuthUser }).user;

  if (!user) {
    throw new ForbiddenError('Not signed in');
  }

  return user;
};
