# Skills

Personal Claude Code skills. Each folder is a skill — symlink the ones you want
into `~/.claude/skills/`.

## Skills

| Skill | Description |
|-------|-------------|
| [clean-code](clean-code/) | Write and review clean code for React, Node.js, Go, TypeScript; verified PR reviews as GitHub drafts or local reports |
| [generate-repo-docs](generate-repo-docs/) | Generate/update repo docs: AGENTS.md, CLAUDE.md, copilot-instructions, docs/*.md |
| [generate-swagger-docs](generate-swagger-docs/) | Add swagger-ui and generate an OpenAPI spec and model schemas |
| [twelve-factor-app](twelve-factor-app/) | Audit a repo for 12-factor compliance (runs only when invoked) |

## Setup

```sh
ln -s ~/Projects/_personal/skills/<skill-name> ~/.claude/skills/<skill-name>
```
