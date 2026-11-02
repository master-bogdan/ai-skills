type EmailTemplate = 'order-cancelled' | 'order-shipped' | 'order-refunded';

type SendEmailInput = {
  to: string;
  template: EmailTemplate;
  data: Record<string, string | number>;
};

export const sendEmail = async ({ to, template, data }: SendEmailInput): Promise<void> => {
  await fetch(`${process.env.EMAIL_API_URL}/send`, {
    method: 'POST',
    body: JSON.stringify({ to, template, data }),
  });
};
