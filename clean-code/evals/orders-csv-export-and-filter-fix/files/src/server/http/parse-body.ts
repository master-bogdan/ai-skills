import type { ZodSchema } from 'zod';
import { ValidationError } from '../errors';

export const parseBody = <T>(schema: ZodSchema<T>, body: unknown): T => {
  const result = schema.safeParse(body);

  if (!result.success) {
    throw new ValidationError(result.error.issues.map((issue) => issue.message).join('; '));
  }

  return result.data;
};
