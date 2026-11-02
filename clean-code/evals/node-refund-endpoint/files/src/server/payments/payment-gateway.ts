type RefundChargeInput = {
  chargeId: string;
  amountCents: number;
  idempotencyKey: string;
};

type RefundChargeResult = {
  refundId: string;
};

export const paymentGateway = {
  refundCharge: async ({ chargeId, amountCents, idempotencyKey }: RefundChargeInput): Promise<RefundChargeResult> => {
    const response = await fetch(`${process.env.PAYMENTS_API_URL}/charges/${chargeId}/refunds`, {
      method: 'POST',
      headers: { 'Idempotency-Key': idempotencyKey, Authorization: `Bearer ${process.env.PAYMENTS_API_KEY}` },
      body: JSON.stringify({ amount: amountCents }),
    });

    if (!response.ok) {
      throw new Error(`Refund for charge ${chargeId} failed with ${response.status}`);
    }

    const body = (await response.json()) as { id: string };
    return { refundId: body.id };
  },
};
