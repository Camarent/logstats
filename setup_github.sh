#!/usr/bin/env bash
#
# One-shot GitHub setup for the `logstats` Week-1 project.
# Run from inside the logstats/ folder on a machine where `gh` is authenticated:
#     gh auth login          # once, if you haven't
#     cd logstats
#     ./setup_github.sh
#
# Creates: a PUBLIC repo, a "Week 1 — Python foundation" milestone,
# labels, and one tracking issue per day. Safe to re-run (skips what exists).

set -euo pipefail

REPO_NAME="logstats"
REPO_DESC="A small, tested CLI that computes stats from log files — Week 1 Python portfolio project."
MILESTONE="Week 1 — Python foundation"

command -v gh >/dev/null || { echo "❌ GitHub CLI (gh) not found. Install it, then 'gh auth login'."; exit 1; }
gh auth status >/dev/null 2>&1 || { echo "❌ Not logged in. Run: gh auth login"; exit 1; }

# 1) Local git repo + first commit ------------------------------------------
if [ ! -d .git ]; then git init -q; fi
git add -A
git commit -q -m "chore: scaffold logstats (README, gitignore, license)" || echo "· nothing new to commit"

# 2) Create the PUBLIC repo and push (skips if it already exists) ------------
if gh repo view "$REPO_NAME" >/dev/null 2>&1; then
  echo "· repo already exists — skipping create"
else
  gh repo create "$REPO_NAME" --public --source=. --remote=origin \
    --description "$REPO_DESC" --push
fi

OWNER_REPO="$(gh repo view --json nameWithOwner -q .nameWithOwner)"
echo "· repo: $OWNER_REPO"

# 3) Labels ------------------------------------------------------------------
mklabel(){ gh label create "$1" --color "$2" --description "$3" --force >/dev/null; }
mklabel week-1  1D76DB "Week 1 build"
mklabel setup   0E8A16 "Project / environment setup"
mklabel feature 5319E7 "New capability"
mklabel testing FBCA04 "Tests & coverage"
mklabel tooling C5DEF5 "Lint / types / packaging"
mklabel docs    0075CA "Documentation"
echo "· labels ready"

# 4) Milestone (via API; ignore error if it already exists) ------------------
gh api "repos/$OWNER_REPO/milestones" -f title="$MILESTONE" \
  -f description="Build a small, tested, typed Python CLI (logstats)." >/dev/null 2>&1 \
  && echo "· milestone created" || echo "· milestone already exists — ok"

# 5) Issues — one per day ----------------------------------------------------
mkissue(){ # title, labels, body
  if gh issue list --search "$1 in:title" --state all --json title -q '.[].title' | grep -qxF "$1"; then
    echo "· issue exists: $1"
  else
    gh issue create --title "$1" --label "$2" --milestone "$MILESTONE" --body "$3" >/dev/null
    echo "· issue created: $1"
  fi
}

mkissue "Day 1 — Project setup + line count" "week-1,setup" '## Goal
Get the repo running and print a line count.

- [ ] `uv init` in this folder; add a `main` entry
- [ ] Read a file with `pathlib.Path.read_text()`, split lines
- [ ] Print the line count
- [ ] Commit + push (first green commit)

**Done when:** `uv run logstats <file>` (or `main.py`) prints a line count.'

mkissue "Day 2 — Types & LogEntry dataclass + --level filter" "week-1,feature" '## Goal
Parse lines into typed records and filter by level.

- [ ] Type hints on every function
- [ ] `@dataclass LogEntry(timestamp, level, message)`
- [ ] Parse each line into a `LogEntry`
- [ ] `--level ERROR` filter

**Done when:** parsing returns typed `LogEntry` objects and filtering works.'

mkissue "Day 3 — Top-N errors (Counter) + requests/hour" "week-1,feature" '## Goal
Idiomatic stdlib stats.

- [ ] Top-N error messages via `collections.Counter`
- [ ] Requests-per-hour bucketing
- [ ] Context managers for file I/O
- [ ] A custom exception for parse errors

**Done when:** the tool reports top-N errors and hourly counts.'

mkissue "Day 4 — pytest suite + package structure" "week-1,testing" '## Goal
Real tests + a proper package.

- [ ] `pytest` with `assert`, fixtures, `parametrize`
- [ ] Meaningful coverage of parsing/stats
- [ ] Refactor into a `logstats/` package (`parser.py`, `stats.py`, `cli.py`)

**Done when:** `uv run pytest` is green with meaningful tests.'

mkissue "Day 5 — click CLI + packaging + README" "week-1,docs" '## Goal
A real CLI, packaged, documented.

- [ ] `click` CLI: `--file`, `--level`, `--top`, `--help`
- [ ] `logging` instead of `print`
- [ ] `pyproject.toml` entry point so `logstats ...` works
- [ ] Finish the README (usage examples)

**Done when:** `logstats --file x.log --level ERROR --top 5` runs, tests green, README done.'

mkissue "Tooling — ruff + mypy clean" "week-1,tooling" '## Goal
Lint + type-check muscle memory (prep for CI in Week 4).

- [ ] Add `ruff` (format + lint) — clean
- [ ] Add `mypy` — clean

**Done when:** `ruff check .` and `mypy .` both pass.'

echo ""
echo "✅ Done. Open it:  gh repo view --web"
echo "   Track work:     gh issue list --milestone \"$MILESTONE\""
echo "   Close from a commit message with:  git commit -m \"...  Closes #1\""
