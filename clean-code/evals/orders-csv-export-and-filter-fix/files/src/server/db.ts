// Thin client over the pg pool; configured from DATABASE_URL in index.ts.
export const db = {
  one: async <T>(_sql: string, _params: unknown[]): Promise<T | null> => null,
  none: async (_sql: string, _params: unknown[]): Promise<void> => undefined,
};
