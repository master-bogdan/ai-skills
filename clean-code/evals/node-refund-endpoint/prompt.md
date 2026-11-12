---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Add a POST /orders/:id/refund endpoint to the server. Body has amountCents, reason, and notifyCustomer (boolean). Only admins can refund. You can't refund more than what's left after previous refunds on the order. It should refund through the payment gateway, record the refund on the order, and email the customer (order-refunded template) if notifyCustomer is true. Build it the same way the existing order endpoints are built.

Input files: the shop-app project (package.json, src/)
