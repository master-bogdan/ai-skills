# docs/architecture.md Contract

Explain system structure, boundaries, and major dependencies.

## Scope

Go deep. Read actual route handlers, services, and models. Produce a doc a new
developer could read to understand the system without asking anyone.

Do not turn this file into:
- coding rules
- type dumps
- review guidance

## Required Sections

- `Purpose` — what this system does and why it exists
- `High-level Shape` — the major layers, services, or components and how they fit together
- `Main Modules or Layers` — what each module owns, its responsibilities, and its boundaries
- `Request Lifecycle` — trace a real representative request end-to-end through the system layers, naming actual files and functions
- `Data Flow` — how data enters, transforms, and exits the system; where it changes shape between layers
- `Runtime Surfaces` — what processes run, what ports they bind, what external services they connect to
- `Key Boundaries` — where trust boundaries, validation boundaries, and layer handoffs occur
- `Key Design Decisions` — why the system is shaped this way; constraints or trade-offs that explain non-obvious choices
- `Recommended Mental Model` — one paragraph a new developer can hold in their head

## Tone

Write for a developer reading this on their first day. Explain the why, not just
the what. Use concrete examples from the actual codebase — real function names,
real file paths, real data shapes.
