---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

On the order details page (src/features/orders/order-details-page.tsx) add an order summary panel. It should show subtotal, discount, tax and total as money, show an "Overdue" badge when the order is past its due date and not paid or shipped yet, and have a search box that filters the line items by name as the user types — debounce it, some orders have hundreds of line items so it should stay snappy. Keep it consistent with the rest of the app.

Input files: the shop-app project (package.json, src/)
