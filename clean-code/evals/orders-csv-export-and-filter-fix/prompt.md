---
tags: [skill-creator]
max_turns: 40
timeout_seconds: 900
allowed_tools: [Read, Glob, Grep, Skill, Write, Edit, Bash]
---

Two things in src/features/orders/order-list.tsx: 1) add an "Export CSV" button to the toolbar that downloads the orders currently shown in the table (columns: order id, customer, total formatted as money, status, created date). 2) there's a bug — when "Active" is selected, cancelled orders still show up; active should mean not shipped and not cancelled. Fix it.

Input files: the shop-app project (package.json, src/)
