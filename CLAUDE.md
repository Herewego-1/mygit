# CLAUDE.md

This file provides guidance to Claude Code and other AI assistants working in this repository.

---

## Project Overview

> **Note:** This repository is currently empty and awaiting initial project setup. Update this section once a language, framework, and purpose have been established.

- **Repository:** `Herewego-1/mygit`
- **Remote origin:** `http://local_proxy@127.0.0.1:54894/git/Herewego-1/mygit`
- **Status:** New — no source code committed yet

When the project is initialized, document here:
- What the project does
- The primary language and framework
- Any relevant architectural decisions

---

## Repository Structure

> Update this section as files and directories are added.

```
mygit/
├── CLAUDE.md          # This file
└── (source files TBD)
```

---

## Git Workflow

### Branch Naming

- **AI-driven branches:** `claude/<purpose>-<session-id>`
  - Example: `claude/claude-md-mm7gqt5uq1a8jbrh-Mvzkk`
- **Feature branches:** `feature/<short-description>`
- **Bug fix branches:** `fix/<short-description>`

### Pushing Changes

Always use the `-u` flag to set the upstream:

```bash
git push -u origin <branch-name>
```

On network failure, retry up to **4 times** with exponential backoff:

| Attempt | Wait before retry |
|---------|-------------------|
| 1       | 2 seconds         |
| 2       | 4 seconds         |
| 3       | 8 seconds         |
| 4       | 16 seconds        |

### Commit Messages

- Use the imperative mood: `Add`, `Fix`, `Update`, `Remove`
- Keep the subject line under 72 characters
- Provide context in the body when the change is non-trivial

### Protected Branches

- **Never force-push** to `main` or `master`
- **Never push** to a branch other than the designated feature branch without explicit user permission
- Resolve merge conflicts rather than discarding changes

### Fetching / Pulling

Prefer fetching a specific branch over a broad fetch:

```bash
git fetch origin <branch-name>
git pull origin <branch-name>
```

---

## Development Commands

> Populate this section once the project is initialized with a build system.

| Task       | Command        |
|------------|----------------|
| Build      | *(TBD)*        |
| Test       | *(TBD)*        |
| Lint       | *(TBD)*        |
| Format     | *(TBD)*        |

Run tests and lint before every commit. Never skip pre-commit hooks (`--no-verify`) unless explicitly instructed.

---

## Code Conventions

> Update this section when a language and framework are chosen.

- Follow the style guide appropriate for the chosen language
- Prefer editing existing files over creating new ones
- Do not add dead code, unused imports, or commented-out blocks
- Keep functions small and focused; extract helpers only when reused in 3+ places

---

## AI Assistant Guidelines

These rules apply to all AI assistants (Claude Code and others) working in this repo.

### Before Making Changes

1. **Read the file first** — always use the Read tool before editing any file
2. **Understand the context** — review surrounding code and related files
3. **Check the branch** — confirm you are on the designated feature branch

### Making Changes

- Keep changes **minimal and focused** on the task at hand
- Do not refactor, add comments, or clean up surrounding code unless explicitly asked
- Do not add error handling, fallbacks, or validation beyond what the task requires
- Do not introduce new dependencies without user approval
- Avoid security vulnerabilities (injection, XSS, insecure defaults)

### Committing

- Stage specific files by name, not `git add -A` or `git add .`
- Write a descriptive commit message explaining *why*, not just *what*
- Mark tasks complete immediately after finishing, not in batch

### Pushing

- Always develop on and push to the designated branch for the session
- The branch must follow the `claude/...` naming convention and match the session ID
- Confirm with the user before any push to a shared or protected branch

### Scope Discipline

- Do not implement features that were not requested
- Do not design for hypothetical future requirements
- Three similar lines of code is better than a premature abstraction
- If blocked, diagnose the root cause — do not brute-force or retry the same failing action

---

## Updating This File

When the project gains source code, CI/CD, or new tooling, update the relevant sections above. Keep this file accurate and concise — it is the primary reference for every AI session in this repository.
