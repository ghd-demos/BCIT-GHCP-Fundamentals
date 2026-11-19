# Copilot Agents Demo

Use the following 3 files to setup your Copilot Agents demo. 
Paste the ISSUE.md file into a new issue in that repository. 

## What this demo shows
- Assign an issue to Copilot to start an agent task
- Monitor progress in AgentHQ
- Re-steer mid-session with a new requirement
- Review the resulting PR like a teammate’s work

## Demo files
- `ISSUE.md` contains the exact issue text to copy/paste into GitHub
- `STEER.md` contains the mid-session requirement change to paste while the agent is working

## Quick demo steps
1. Create a new GitHub Issue by copying the Title and Body from `ISSUE.md`
2. Assign the issue to Copilot to start the agent task
3. Open AgentHQ to monitor progress
4. Paste `STEER.md` into the agent session to re-steer the work
5. Review the PR diff for clarity, completeness, and constraints.
6. Verify the PR edited the README.md file by adding priority levels plus the steered examples. 

---

## Ticket Triage Policy

Severity describes impact; Priority sets response order. Reassess the default when urgency or scope warrants it.

### Severity
- Low: minor annoyance with an easy workaround
- Medium: meaningful user impact, but workarounds exist
- High: blocks key workflows or causes data loss

### Priority
- P0: critical, widespread outage or active data loss; respond immediately
- P1: urgent, blocks key workflows; default for High severity
- P2: important, meaningful impact with a workaround; default for Medium
- P3: routine, minor impact with an easy workaround; default for Low

Use P0 only when immediate, broad impact makes the normal severity default too slow.

### How to triage in 60 seconds
1. Identify who is affected and what is blocked or at risk.
2. Set Severity, then use its default Priority (High→P1, Medium→P2, Low→P3).
3. Escalate to P0 for a critical, widespread incident; note why.
4. Record the owner and next action; revisit priority if impact changes.
