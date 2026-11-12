import type { ReactNode } from 'react';

type BadgeProps = {
  variant?: 'neutral' | 'warning' | 'danger' | 'success';
  children: ReactNode;
};

export function Badge({ variant = 'neutral', children }: BadgeProps) {
  return <span className={`badge badge-${variant}`}>{children}</span>;
}
