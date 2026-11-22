# Starting a project agent in Orca

## 1. Planning (once per project)
Open a Claude Code session in the repo and paste:

> Read CLAUDE.md, BRIEF.md, DECISIONS.md and HARDWARE.md. Before changing anything, list
> EVERY question you would need answered to work unattended for several days: keys,
> devices, IPs, ports, limits, scope, decisions, and how each task's "done" is checked.
> One numbered list. Then stop.

Answer the list once. Then:

> Write my answers into DECISIONS.md, HARDWARE.md and .env.example (names only), fix
> BRIEF.md and check.sh if needed, commit on the current branch, and stop.

## 2. The loop (every run)

> Read CLAUDE.md, BRIEF.md, PROGRESS.md and DECISIONS.md. Work through the unchecked tasks
> in order, following CLAUDE.md exactly: one branch and one PR per task, ./check.sh must
> pass, update PROGRESS.md each time. If you're missing anything, write it to QUESTIONS.md
> and move on — never stop to wait. Stop after <N> tasks or when every task is ticked.

Start with N = 3 while the brief settles, then raise to 10 for overnight runs.

## 3. Optional: hands-off repeats with open-ralph-wiggum
`ralph "<loop prompt above> Output <promise>DONE</promise> when every task is ticked." --agent claude-code --max-iterations 10`
