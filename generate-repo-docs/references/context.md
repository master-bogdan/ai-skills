# CONTEXT.md Contract

Domain language glossary for the repo. Defines the canonical terms used by the
codebase, prevents naming drift, and resolves ambiguities.

## Audience

Both AI agents and humans — but especially AI agents. A well-written CONTEXT.md
lets agents use the same vocabulary as the team, which makes suggestions and
docs more precise and less generic.

## When to generate or update

- **Create** if no `CONTEXT.md` exists and the repo has meaningful domain concepts
- **Update** if `CONTEXT.md` exists — add missing terms found in the codebase, never remove or overwrite existing entries. Existing terms may reflect manual curation or resolved ambiguities that can't be reconstructed from code.
- **Skip** and mark `Needs confirmation` if the repo is a utility library, toolchain, or infrastructure project with no business domain language
- If multiple bounded contexts exist, create `CONTEXT-MAP.md` at root plus individual `CONTEXT.md` files per context

## How to populate

Read the codebase for recurring domain terms: entity names, status values,
business operations, named flows, and concepts that appear across multiple
layers. Only include terms specific to this project's domain — not general
programming concepts.

## Required structure

```md
# {Context Name}

{One or two sentences describing what domain this context covers.}

## Language

**Order**:
A customer's request to purchase one or more items.
_Avoid_: Purchase, transaction, cart

**Invoice**:
A request for payment generated after fulfillment is confirmed.
_Avoid_: Bill, payment request

## Relationships

- An **Order** produces one or more **Invoices**
- An **Invoice** belongs to exactly one **Customer**

## Flagged ambiguities

- "account" was used to mean both **Customer** and **User** — resolved: these are distinct concepts
```

## Rules

- One sentence per definition — what it IS, not what it does
- List avoided synonyms under each term
- Show relationships with cardinality where obvious
- Flag and resolve ambiguities explicitly
- Keep domain-specific only — no general programming terms
- Never duplicate AGENTS.md or architecture.md content
