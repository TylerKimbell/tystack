# tystack: agent instructions

tystack is a plugin of general agent skills that work in any project without setup. It runs as a plugin in claude.ai, Cowork, and Claude Code, and as plain skill folders in Codex. The repo is public.

`README.md` is for people who install the skills. This file is for changing them. It is the instructions file for Claude Code and Codex; `CLAUDE.md` holds only `@AGENTS.md`. Both are for sessions in this repo. Neither is loaded for people who install the plugin, which is why the plugin validator warns about a `CLAUDE.md` at a plugin's root. That warning is expected.

## What belongs here

- **General skills only.** A skill works in any project with no setup. One that needs a company's process, a project's layout, or one project's config belongs in that project.
- **Nothing that names a company.** The repo is public, so no file names a company, its product, its people, or its clients. Examples and fixtures use invented names. Real transcripts used as eval fixtures stay in `evals/<name>/local/`, which Git ignores. Never commit them.
- **Works in Claude and Codex.** A skill names a Claude-only tool beside a generic form and a fallback, for example "start a helper agent (in Claude Code, the Agent tool); with no helper agents, do the step yourself". Codex-only settings go in the skill's `agents/openai.yaml`.
- **A project's instructions win.** A skill defers to the project's own instructions and house style where they conflict with its defaults.

## Layout

```
.claude-plugin/     plugin.json (name, version, description) and marketplace.json
skills/<name>/      SKILL.md, the files it loads, and agents/openai.yaml for Codex settings
evals/<name>/       The iterate spec (iterate.md), its log, fixtures, and check.py for
                    improving that skill. Never loaded as part of a skill.
.github/workflows/  CI: every check.py, then the manifest validator
README.md           Skills table, install steps, and how projects override the defaults
AGENTS.md           Instructions (this file). CLAUDE.md imports it.
```

## Change together

| When this changes | Also update, in the same change |
|---|---|
| A skill's behavior | `version` in `.claude-plugin/plugin.json`. Installed copies update only when it changes, so a behavior change with no bump reaches nobody |
| A skill is added, renamed, or removed | The skills table in `README.md`, the descriptions in `plugin.json` and `marketplace.json`, and the install text in `README.md` that names skills |
| How a skill runs (automatic or on request only) | `disable-model-invocation` in its `SKILL.md` for Claude, `allow_implicit_invocation` in its `agents/openai.yaml` for Codex, its row in the `README.md` table, and the install text that says how to call it |
| A skill's name, purpose, or trigger | Its `SKILL.md` description, and `display_name`, `short_description`, and `default_prompt` in its `agents/openai.yaml`, where the file has them |
| A skill that has `evals/<name>/` | Run `python3 evals/<name>/check.py`, and update the spec or fixtures the change outdates |
| A skill adapted from another project | The attribution comment in its `SKILL.md`, and the credits in `README.md` and `LICENSE` |

## Checks

Run these before a commit. CI runs both on every push and pull request.

- `python3 evals/<name>/check.py` for each skill that has evals, and before each `iterate` round on that skill. It uses the standard library only. A check that needs the private fixtures in `evals/<name>/local/` skips those parts where the folder is missing, and says so.
- `claude plugin validate .` for the manifests, where the `claude` command is installed. It needs no sign-in.

## Git workflow

- Commit and push only when the user asks.
- A change goes through a branch and a pull request, merged with a merge commit. Don't push to `main`.
- Write prose plainly: lead with the point, no filler. Run `unslop` on anything a person reads, including a skill's text, the README, a commit message, and a pull request description. Where the skill is not installed, read `skills/unslop/SKILL.md` and follow it.
