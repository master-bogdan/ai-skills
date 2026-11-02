import type { InputHTMLAttributes } from 'react';

type InputProps = InputHTMLAttributes<HTMLInputElement> & {
  label: string;
};

export function Input({ label, id, ...props }: InputProps) {
  return (
    <label htmlFor={id} className="field">
      <span className="field-label">{label}</span>
      <input id={id} className="field-input" {...props} />
    </label>
  );
}
