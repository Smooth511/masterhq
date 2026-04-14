# Troubleshooting Guide: GitHub Copilot Agent Behavior

**Repository:** Smooth511/Claude-MKII  
**Last Updated:** 2026-03-18

---

## Quick Reference

| Problem | Cause | Fix |
|---------|-------|-----|
| Wrong model (GPT/Sonnet) appears | Model routing is platform-controlled | Check `.github/agents/ClaudeMKII.agent.md` has `model: claude-opus-4.5` |
| Duplicate PRs | Separate chats = separate agents | Keep one chat alive for multi-step tasks |
| Agent ignores instructions | Instructions loaded after model selected | Model lock must be in YAML frontmatter |
| Work lost after disable/enable | Platform doesn't resume queued jobs | Don't disable mid-task |
| Agent refuses to commit token | Platform safety policy | Use GitHub Secrets instead |

---

## 1. Why Do Different Models Appear?

### The Two Models

When using GitHub Copilot, there are actually **two separate model assignments**:

1. **Chat Model** - The model you're talking to in the conversation
2. **Coding Agent Model** - The model that executes when you confirm a tool-run or PR creation

These are assigned separately by GitHub's backend.

### How Each Is Determined

**Chat Model:**
- Determined by GitHub's routing system
- Considers: account tier, feature flags, availability, load balancing
- Can vary between conversations
- You cannot directly control this

**Coding Agent Model:**
- Determined by `.github/agents/[AgentName].agent.md` YAML frontmatter
- Specifically the `model:` field
- This is enforceable

### Verifying Your Model

**For chat:** Ask "What model are you?"

**For coding agent:** Check the agent config:
```yaml
---
name: ClaudeMKII
model: claude-opus-4.5   # ← This controls coding agent model
---
```

If `model:` is missing, GitHub picks a default (often Sonnet).

---

## 2. Why Do Duplicate PRs Keep Getting Created?

### Root Cause

Each new chat conversation spawns a **completely isolated agent session**. Agents cannot see:
- Other active chats
- Other pending PRs (unless they search for them)
- Work in progress from other sessions

### How It Happens

1. You start Chat A, ask for Feature X
2. Agent in Chat A creates PR #1 for Feature X
3. Chat A times out or you start Chat B
4. You ask Chat B for Feature X (same thing)
5. Agent in Chat B creates PR #2 for Feature X

Both agents followed instructions. Neither knew about the other.

### Prevention

1. **Keep one chat alive** for multi-step tasks
2. **Don't restart** - if you need clarification, ask in the same chat
3. **Check PR list** before starting a new chat: `gh pr list --state open`
4. **Explicitly tell the agent** about existing PRs: "PR #X already started this, continue from there"

### What Instructions Can Do

The agent can be instructed to:
- Check for existing PRs before creating new ones
- Ask before creating a PR
- Report if similar work exists

But these only work **within that agent's session** - they don't prevent a different session from starting.

---

## 3. Why Do Agents Ignore Repository Instructions?

### Timing Issue

Instructions in `.github/copilot-instructions.md` are loaded **after** the model is already assigned. This means:

- "Sonnet is banned" - Only works if an Opus agent reads it
- "Use model X" - Has no effect (model already selected)

### What Actually Works

| Instruction Type | Where to Put It | Enforced By |
|-----------------|-----------------|-------------|
| Model selection | `.github/agents/*.agent.md` YAML frontmatter | GitHub platform |
| Behavioral rules | `.github/copilot-instructions.md` | The agent itself |
| Access control | `AGENT_ACCESS.md` | The agent itself (requires reading) |

### The Model Lock

```yaml
# In .github/agents/ClaudeMKII.agent.md
---
name: ClaudeMKII
model: claude-opus-4.5   # ← Platform reads this BEFORE loading instructions
---
```

This is the **only reliable way** to control which model runs coding agent tasks.

---

## 4. What Happens When You Disable/Re-enable the Coding Agent?

### When You Disable

1. Currently running jobs may be cancelled
2. Queued jobs are dropped
3. In-progress work is orphaned (branch exists, PR may be partial)
4. Agent sessions are terminated

### When You Re-enable

1. **Nothing resumes** - previous state is lost
2. New tasks start fresh
3. You may need to manually close/clean up partial PRs

### Why Work Gets "Lost"

The 3-hour investigation incident:
1. Coding agent was in the middle of work
2. Agent was disabled
3. Platform terminated the session
4. When re-enabled, the platform had no memory of the previous task
5. User had to restart from scratch

### Prevention

1. Don't disable mid-task
2. If you must disable, wait for current work to complete
3. Check for partial PRs after re-enabling: `gh pr list --state all`

---

## 5. Why Won't Agents Commit Tokens/Secrets?

### Platform Safety Policy

GitHub Copilot agents have built-in restrictions against committing secrets:
- API keys
- Tokens (especially `ghp_*` patterns)
- Passwords
- Private keys

This is **not controlled by repository instructions** - it's a platform-level policy.

### What Happens

1. You provide a token
2. Agent recognizes it as a secret
3. Agent refuses to commit it
4. Even if you explicitly order it, platform policy overrides

### Alternatives

| Method | Pros | Cons |
|--------|------|------|
| GitHub Secrets | Secure, agents can reference | Requires repo settings access |
| Environment variables | Standard practice | Requires workflow setup |
| Manual push | Works immediately | Exposes secret in commit history |

### Recommended: GitHub Secrets

1. Go to repo → Settings → Secrets and variables → Actions
2. Add your secret
3. Reference in workflows: `${{ secrets.YOUR_SECRET }}`

Agents can read instructions about which secrets to use, but cannot commit the actual values.

---

## 6. Verification Checklist

Run these checks when experiencing issues:

```bash
# Check agent config has model lock
cat .github/agents/ClaudeMKII.agent.md | head -10

# Check for open PRs (potential duplicates)
gh pr list --state open

# Check recent commits for unexpected changes
git log --oneline -10

# Verify instructions file exists and is correct
head -20 .github/copilot-instructions.md
```

### Expected Output

Agent config should show:
```yaml
---
name: ClaudeMKII
model: claude-opus-4.5
---
```

Instructions file should start with:
```markdown
# ClaudeMKII Core Memory
This file auto-loads as copilot instructions...
```

---

## 7. Quick Fixes

### "Agent is using wrong model"
1. Check `.github/agents/ClaudeMKII.agent.md` has `model: claude-opus-4.5`
2. If missing, add it and commit
3. Start a new chat (old chats keep old routing)

### "Duplicate PRs appeared"
1. Check which PR has more complete work
2. Close the others with comment "Duplicate of #X"
3. Continue work in surviving PR

### "Agent isn't following instructions"
1. Verify `.github/copilot-instructions.md` exists
2. Verify it has no syntax errors (check for unclosed markdown)
3. Ask agent to explicitly read and confirm it loaded

### "Work disappeared"
1. Check if a PR exists: `gh pr list --state all`
2. Check if a branch exists: `git branch -r`
3. If yes, resume work on that branch
4. If no, work is lost - restart

---

*Guide maintained by ClaudeMKII. Update this file when new patterns are discovered.*
