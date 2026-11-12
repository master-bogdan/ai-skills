# Conventions brief

The repo documents no coding standards, so its conventions live in its code. You find where the change **drifts**
from them.

For each new or substantially changed file, open 2 sibling files of the same kind (component next to component,
service next to service) and compare: file naming, export style, function style (declaration or arrow), `type` or
`interface`, error handling, where validation happens, layering (router → controller → service → repository), and
test style. Each divergence the change introduced is a finding citing the sibling it differs from, with `path:line`.
A pattern the project doesn't use is drift, even when it's a good pattern.

Report in the format of [finding.md](finding.md). Done when every new or substantially changed file was compared with
two named siblings.
